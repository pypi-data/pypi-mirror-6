# Copyright (C) 2011-2014 2ndQuadrant Italia (Devise.IT S.r.L.)
#
# This file is part of Barman.
#
# Barman is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Barman is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Barman.  If not, see <http://www.gnu.org/licenses/>.

''' This module represents a backup. '''

from glob import glob
import datetime
import logging
import os
import sys
import shutil
import time
import tempfile
import re
from barman.infofile import WalFileInfo, BackupInfo, UnknownBackupIdException
from barman.fs import UnixLocalCommand, UnixRemoteCommand, FsOperationFailed

import dateutil.parser

from barman import xlog, output
from barman.command_wrappers import RsyncPgData
from barman.compression import CompressionManager, CompressionIncompatibility
from barman.hooks import HookScriptRunner


_logger = logging.getLogger(__name__)


class BackupManager(object):
    '''Manager of the backup archive for a server'''

    DEFAULT_STATUS_FILTER = (BackupInfo.DONE,)
    DANGEROUS_OPTIONS = ['data_directory', 'config_file', 'hba_file',
            'ident_file', 'external_pid_file', 'ssl_cert_file',
            'ssl_key_file', 'ssl_ca_file', 'ssl_crl_file',
            'unix_socket_directory']
    def __init__(self, server):
        '''Constructor'''
        self.name = "default"
        self.server = server
        self.config = server.config
        self.available_backups = {}
        self.compression_manager = CompressionManager(self.config)

        # used for error messages
        self.current_action = None

    def get_available_backups(self, status_filter=DEFAULT_STATUS_FILTER):
        '''
        Get a list of available backups

        :param status_filter: default DEFAULT_STATUS_FILTER. The status of the backup list returned
        '''
        if not isinstance(status_filter, tuple):
            status_filter = tuple(status_filter,)
        if status_filter not in self.available_backups:
            available_backups = {}
            for filename in glob("%s/*/backup.info" % self.config.basebackups_directory):
                backup = BackupInfo(self.server, filename)
                if backup.status not in status_filter:
                        continue
                available_backups[backup.backup_id] = backup
            self.available_backups[status_filter] = available_backups
            return available_backups
        else:
            return self.available_backups[status_filter]

    def get_previous_backup(self, backup_id, status_filter=DEFAULT_STATUS_FILTER):
        '''
        Get the previous backup (if any) in the catalog

        :param status_filter: default DEFAULT_STATUS_FILTER. The status of the backup returned
        '''
        if not isinstance(status_filter, tuple):
            status_filter = tuple(status_filter)
        backup = BackupInfo(self.server, backup_id=backup_id)
        available_backups = self.get_available_backups(status_filter + (backup.status,))
        ids = sorted(available_backups.keys())
        try:
            current = ids.index(backup_id)
            while current > 0:
                res = available_backups[ids[current - 1]]
                if res.status in status_filter:
                    return res
                current -= 1
            else:
                return None
        except ValueError:
            raise UnknownBackupIdException('Could not find backup_id %s' % backup_id)

    def get_next_backup(self, backup_id, status_filter=DEFAULT_STATUS_FILTER):
        '''
        Get the next backup (if any) in the catalog

        :param status_filter: default DEFAULT_STATUS_FILTER. The status of the backup returned
        '''
        if not isinstance(status_filter, tuple):
            status_filter = tuple(status_filter)
        backup = BackupInfo(self.server, backup_id=backup_id)
        available_backups = self.get_available_backups(status_filter + (backup.status,))
        ids = sorted(available_backups.keys())
        try:
            current = ids.index(backup_id)
            while current < (len(ids) - 1):
                res = available_backups[ids[current + 1]]
                if res.status in status_filter:
                    return res
                current += 1
            else:
                return None
        except ValueError:
            raise UnknownBackupIdException('Could not find backup_id %s' % backup_id)

    def get_last_backup(self, status_filter=DEFAULT_STATUS_FILTER):
        '''
        Get the last backup (if any) in the catalog

        :param status_filter: default DEFAULT_STATUS_FILTER. The status of the backup returned
        '''
        available_backups = self.get_available_backups(status_filter)
        if len(available_backups) == 0:
            return None

        ids = sorted(available_backups.keys())
        return ids[-1]

    def get_first_backup(self, status_filter=DEFAULT_STATUS_FILTER):
        '''
        Get the first backup (if any) in the catalog

        :param status_filter: default DEFAULT_STATUS_FILTER. The status of the backup returned
        '''
        available_backups = self.get_available_backups(status_filter)
        if len(available_backups) == 0:
            return None

        ids = sorted(available_backups.keys())
        return ids[0]

    def delete_backup(self, backup):
        '''
        Delete a backup

        :param backup: the backup to delete
        '''
        available_backups = self.get_available_backups()
        # Honour minimum required redundancy
        if backup.status == BackupInfo.DONE and self.server.config.minimum_redundancy >= len(available_backups):
            yield "Skipping delete of backup %s for server %s due to minimum redundancy requirements (%s)" % (
                backup.backup_id, self.config.name, self.server.config.minimum_redundancy)
            _logger.warning("Could not delete backup %s for server %s - minimum redundancy = %s, current size = %s"
                % (backup.backup_id, self.config.name, self.server.config.minimum_redundancy, len(available_backups)))
            return

        yield "Deleting backup %s for server %s" % (backup.backup_id, self.config.name)
        previous_backup = self.get_previous_backup(backup.backup_id)
        next_backup = self.get_next_backup(backup.backup_id)
        # remove the backup
        self.delete_basebackup(backup)
        if not previous_backup:  # backup is the first one
            yield "Delete associated WAL segments:"
            remove_until = None
            if next_backup:
                remove_until = next_backup.begin_wal
            with self.server.xlogdb() as fxlogdb:
                xlogdb_new = fxlogdb.name + ".new"
                with open(xlogdb_new, 'w') as fxlogdb_new:
                    for line in fxlogdb:
                        name, _, _, _ = self.server.xlogdb_parse_line(line)
                        if remove_until and name >= remove_until:
                            fxlogdb_new.write(line)
                            continue
                        else:
                            yield "\t%s" % name
                            # Delete the WAL segment
                            self.delete_wal(name)
                shutil.move(xlogdb_new, fxlogdb.name)
        yield "Done"

    def backup(self, immediate_checkpoint):
        """
        Performs a backup for the server
        """
        _logger.debug("initialising backup information")
        backup_stamp = datetime.datetime.now()
        self.current_action = "starting backup"
        backup_info = None
        try:
            backup_info = BackupInfo(
                self.server,
                backup_id=backup_stamp.strftime('%Y%m%dT%H%M%S'))
            backup_info.save()
            output.info(
                "Starting backup for server %s in %s",
                self.config.name,
                backup_info.get_basebackup_directory())

            # Run the pre-backup-script if present.
            script = HookScriptRunner(self, 'backup_script', 'pre')
            script.env_from_backup_info(backup_info)
            script.run()

            # Start the backup
            self.backup_start(backup_info, immediate_checkpoint)
            backup_info.set_attribute("begin_time", backup_stamp)
            backup_info.save()
            output.info("Backup start at xlog location: %s (%s, %08X)",
                            backup_info.begin_xlog,
                            backup_info.begin_wal,
                            backup_info.begin_offset)

            self.current_action = "copying files"
            try:
                # Start the copy
                output.info("Copying files.")
                backup_size = self.backup_copy(backup_info)
                backup_info.set_attribute("size", backup_size)
                output.info("Copy done.")
            except:
                raise
            else:
                self.current_action = "issuing stop of the backup"
                output.info("Asking PostgreSQL server to finalize the backup.")
            finally:
                self.backup_stop(backup_info)

            backup_info.set_attribute("status", "DONE")

        except:
            if backup_info:
                backup_info.set_attribute("status", "FAILED")
                backup_info.set_attribute("error", "failure %s" % self.current_action)

            msg = "Backup failed %s" % self.current_action
            output.exception(msg)

        else:
            output.info("Backup end at xlog location: %s (%s, %08X)",
                            backup_info.end_xlog,
                            backup_info.end_wal,
                            backup_info.end_offset)
            output.info("Backup completed")
        finally:
            if backup_info:
                backup_info.save()

                # Run the post-backup-script if present.
                script = HookScriptRunner(self, 'backup_script', 'post')
                script.env_from_backup_info(backup_info)
                script.run()

        output.result('backup', backup_info)

    def recover(self, backup, dest, tablespaces, target_tli, target_time, target_xid, target_name, exclusive, remote_command):
        '''
        Performs a recovery of a backup

        :param backup: the backup to recover
        :param dest: the destination directory
        :param tablespaces: a dictionary of tablespaces
        :param target_tli: the target timeline
        :param target_time: the target time
        :param target_xid: the target xid
        :param target_name: the target name created previously with pg_create_restore_point() function call
        :param exclusive: whether the recovery is exclusive or not
        :param remote_command: default None. The remote command to recover the base backup,
                               in case of remote backup.
        '''
        for line in self.cron(False):
            yield line

        recovery_dest = 'local'

        if remote_command:
            recovery_dest = 'remote'
            rsync = RsyncPgData(ssh=remote_command,
                                bwlimit=self.config.bandwidth_limit,
                                network_compression=self.config.network_compression)
            try:
                # create a UnixRemoteCommand obj if is a remote recovery
                cmd = UnixRemoteCommand(remote_command)
            except FsOperationFailed:
                output.error(
                    "Unable to connect to the target host using the command "
                    "'%s'" % remote_command
                )
                return
        else:
            # if is a local recovery create a UnixLocalCommand
            cmd = UnixLocalCommand()
        msg = "Starting %s restore for server %s using backup %s " % (recovery_dest, self.config.name, backup.backup_id)
        yield msg
        _logger.info(msg)

        msg = "Destination directory: %s" % dest
        yield msg
        _logger.info(msg)
        if backup.tablespaces:
            try:
                tblspc_dir = os.path.join(dest, 'pg_tblspc')
                # check for pg_tblspc dir into recovery destination folder.
                # if does not exists, create it
                cmd.create_dir_if_not_exists(tblspc_dir)
            except FsOperationFailed:
                msg = "ERROR: unable to initialize Tablespace Recovery Operation "
                _logger.critical(msg)
                info = sys.exc_info()[0]
                _logger.critical(info)
                raise SystemExit(msg)

            for name, oid, location in backup.tablespaces:
                try:
                    # check if relocation is needed
                    if name in tablespaces:
                        location = tablespaces[name]

                    tblspc_file = os.path.join(tblspc_dir, str(oid))
                    # delete destination directory for symlink file if exists
                    cmd.delete_dir_if_exists(tblspc_file)
                    # check that destination dir for tablespace exists
                    cmd.check_directory_exists(location)
                    # create it if does not exists
                    cmd.create_dir_if_not_exists(location)
                    # check for write permission into destination directory)
                    cmd.check_write_permission(location)
                    # create symlink between tablespace and recovery folder
                    cmd.create_symbolic_link(location,tblspc_file)
                except FsOperationFailed:
                    msg = "ERROR: unable to prepare '%s' tablespace (destination '%s')" % (name, location)
                    _logger.critical(msg)
                    info = sys.exc_info()[0]
                    _logger.critical(info)
                    raise SystemExit(msg)

                yield "\t%s, %s, %s" % (oid, name, location)

        wal_dest = os.path.join(dest, 'pg_xlog')
        target_epoch = None
        target_datetime = None
        if target_time:
            try:
                target_datetime = dateutil.parser.parse(target_time)
            except:
                msg = "ERROR: unable to parse the target time parameter %r" % target_time
                _logger.critical(msg)
                raise SystemExit(msg)
            target_epoch = time.mktime(target_datetime.timetuple()) + (target_datetime.microsecond / 1000000.)
        if target_time or target_xid or (target_tli and target_tli != backup.timeline) or target_name:
            targets = {}
            if target_time:
                targets['time'] = str(target_datetime)
            if target_xid:
                targets['xid'] = str(target_xid)
            if target_tli and target_tli != backup.timeline:
                targets['timeline'] = str(target_tli)
            if target_name:
                targets['name'] = str(target_name)
            yield "Doing PITR. Recovery target %s" % \
                (", ".join(["%s: %r" % (k, v) for k, v in targets.items()]))
            wal_dest = os.path.join(dest, 'barman_xlog')

        # Copy the base backup
        msg = "Copying the base backup."
        yield msg
        _logger.info(msg)
        self.recover_basebackup_copy(backup, dest, remote_command)
        _logger.info("Base backup copied.")

        # Prepare WAL segments local directory
        msg = "Copying required wal segments."
        _logger.info(msg)
        yield msg

        # Retrieve the list of required WAL segments according to recovery options
        xlogs = {}
        required_xlog_files = tuple(self.server.get_required_xlog_files(backup, target_tli, target_epoch))
        for filename in required_xlog_files:
            hashdir = xlog.hash_dir(filename)
            if hashdir not in xlogs:
                xlogs[hashdir] = []
            xlogs[hashdir].append(filename)
        # Check decompression options
        compressor = self.compression_manager.get_compressor()

        # Restore WAL segments
        self.recover_xlog_copy(compressor, xlogs, wal_dest, remote_command)
        _logger.info("Wal segmets copied.")

        # Generate recovery.conf file (only if needed by PITR)
        if target_time or target_xid or (target_tli and target_tli != backup.timeline) or target_name:
            msg = "Generating recovery.conf"
            yield  msg
            _logger.info(msg)
            if remote_command:
                tempdir = tempfile.mkdtemp(prefix='barman_recovery-')
                recovery = open(os.path.join(tempdir, 'recovery.conf'), 'w')
            else:
                recovery = open(os.path.join(dest, 'recovery.conf'), 'w')
            print >> recovery, "restore_command = 'cp barman_xlog/%f %p'"
            print >> recovery, "recovery_end_command = 'rm -fr barman_xlog'"
            if target_time:
                print >> recovery, "recovery_target_time = '%s'" % target_time
            if target_tli:
                print >> recovery, "recovery_target_timeline = %s" % target_tli
            if target_xid:
                print >> recovery, "recovery_target_xid = '%s'" % target_xid
            if target_name:
                print >> recovery, "recovery_target_name = '%s'" % target_name
            if (target_xid or target_time) and exclusive:
                print >> recovery, "recovery_target_inclusive = '%s'" % (not exclusive)
            recovery.close()
            if remote_command:
                recovery = rsync.from_file_list(['recovery.conf'], tempdir, ':%s' % dest)
                shutil.rmtree(tempdir)
            _logger.info('recovery.conf generated')
        else:
            # avoid shipping of just recovered pg_xlog files
            if remote_command:
                status_dir = tempfile.mkdtemp(prefix='barman_xlog_status-')
            else:
                status_dir = os.path.join(wal_dest, 'archive_status')
                os.makedirs(status_dir) # no need to check, it must not exist
            for filename in required_xlog_files:
                with open(os.path.join(status_dir, "%s.done" % filename), 'a') as f:
                    f.write('')
            if remote_command:
                retval = rsync('%s/' % status_dir, ':%s' % os.path.join(wal_dest, 'archive_status'))
                if retval != 0:
                    msg = "WARNING: unable to populate pg_xlog/archive_status dorectory"
                    yield msg
                    _logger.warning(msg)
                shutil.rmtree(status_dir)


        # Disable dangerous setting in the target data dir
        if remote_command:
            tempdir = tempfile.mkdtemp(prefix='barman_recovery-')
            pg_config = os.path.join(tempdir, 'postgresql.conf')
            shutil.copy2(os.path.join(backup.get_basebackup_directory(), 'pgdata', 'postgresql.conf'), pg_config)
        else:
            pg_config = os.path.join(dest, 'postgresql.conf')
        if self.pg_config_mangle(pg_config,
                              {'archive_command': 'false'},
                              "%s.origin" % pg_config):
            msg = "The archive_command was set to 'false' to prevent data losses."
            yield msg
            _logger.info(msg)

        # Find dangerous options in the configuration file (locations)
        clashes = self.pg_config_detect_possible_issues(pg_config)

        if remote_command:
            recovery = rsync.from_file_list(['postgresql.conf', 'postgresql.conf.origin'], tempdir, ':%s' % dest)
            shutil.rmtree(tempdir)


        yield ""
        yield "Your PostgreSQL server has been successfully prepared for recovery!"
        yield ""
        yield "Please review network and archive related settings in the PostgreSQL"
        yield "configuration file before starting the just recovered instance."
        yield ""
        if clashes:
            yield "WARNING: Before starting up the recovered PostgreSQL server,"
            yield "please review also the settings of the following configuration"
            yield "options as they might interfere with your current recovery attempt:"
            yield ""

            for name, value in sorted(clashes.items()):
                yield "    %s = %s" % (name, value)

            yield ""
        _logger.info("Recovery completed successful.")


    def cron(self, verbose):
        '''
        Executes maintenance operations, such as WAL trashing.

        :param verbose: print some information
        '''
        found = False
        compressor = self.compression_manager.get_compressor()
        with self.server.xlogdb('a') as fxlogdb:
            if verbose:
                yield "Processing xlog segments for %s" % self.config.name
            available_backups = self.get_available_backups(BackupInfo.STATUS_ALL)
            for filename in sorted(glob(os.path.join(self.config.incoming_wals_directory, '*'))):
                if not found and not verbose:
                    yield "Processing xlog segments for %s" % self.config.name
                found = True
                if not len(available_backups):
                    msg = "No base backup available. Trashing file %s" % os.path.basename(filename)
                    yield "\t%s" % msg
                    _logger.warning(msg)
                    os.unlink(filename)
                    continue
                # Archive the WAL file
                wal_info = self.cron_wal_archival(compressor, filename)

                # Updates the information of the WAL archive with the latest segement's
                fxlogdb.write(wal_info.to_xlogdb_line())
                _logger.info('Processed file %s', filename)
                yield "\t%s" % os.path.basename(filename)
        if not found and verbose:
            yield "\tno file found"

        # Retention policy management
        if self.server.enforce_retention_policies and self.config.retention_policy_mode == 'auto':
            available_backups = self.get_available_backups(BackupInfo.STATUS_ALL)
            retention_status = self.config.retention_policy.report()
            for bid in sorted(retention_status.iterkeys()):
                if retention_status[bid] == BackupInfo.OBSOLETE:
                    _logger.info("Enforcing retention policy: removing backup %s for server %s" % (
                        bid, self.config.name))
                    for line in self.delete_backup(available_backups[bid]):
                        yield line

    def delete_basebackup(self, backup):
        '''
        Delete the given base backup

        :param backup: the backup to delete
        '''
        backup_dir = backup.get_basebackup_directory();
        shutil.rmtree(backup_dir)

    def delete_wal(self, name):
        '''
        Delete a WAL segment, with the given name

        :param name: the name of the WAL to delete
        '''
        hashdir = os.path.join(self.config.wals_directory, xlog.hash_dir(name))
        try:
            os.unlink(os.path.join(hashdir, name))
            try:
                os.removedirs(hashdir)
            except:
                pass
        except:
            _logger.warning('Expected WAL file %s not found during delete',
                name)

    def backup_start(self, backup_info, immediate_checkpoint):
        '''
        Start of the backup

        :param backup_info: the backup information structure
        '''
        self.current_action = "connecting to database (%s)" % self.config.conninfo
        _logger.debug(self.current_action)

        # Set the PostgreSQL data directory
        self.current_action = "detecting data directory"
        _logger.debug(self.current_action)
        data_directory = self.server.get_pg_setting('data_directory')
        backup_info.set_attribute('pgdata', data_directory)

        # Set server version
        backup_info.set_attribute('version', self.server.server_version)

        # Set configuration files location
        cf = self.server.get_pg_configuration_files()
        if cf:
            for key in sorted(cf.keys()):
                backup_info.set_attribute(key, cf[key])

        # Get tablespaces information
        self.current_action = "detecting tablespaces"
        _logger.debug(self.current_action)
        tablespaces = self.server.get_pg_tablespaces()
        if tablespaces and len(tablespaces) > 0:
            backup_info.set_attribute("tablespaces", tablespaces)
            for oid, name, location in tablespaces:
                msg = "\t%s, %s, %s" % (oid, name, location)
                _logger.info(msg)

        # Issue pg_start_backup on the PostgreSQL server
        self.current_action = "issuing pg_start_backup command"
        _logger.debug(self.current_action)
        backup_label = ("Barman backup %s %s"
                        % (backup_info.server_name, backup_info.backup_id))
        start_row = self.server.pg_start_backup(backup_label,
                                                immediate_checkpoint)
        if start_row:
            start_xlog, start_file_name, start_file_offset = start_row
            backup_info.set_attribute("status", "STARTED")
            backup_info.set_attribute("timeline", int(start_file_name[0:8], 16))
            backup_info.set_attribute("begin_xlog", start_xlog)
            backup_info.set_attribute("begin_wal", start_file_name)
            backup_info.set_attribute("begin_offset", start_file_offset)
        else:
            self.current_action = "starting the backup: PostgreSQL server is already in exclusive backup mode"
            raise Exception('concurrent exclusive backups are not allowed')

    def backup_copy(self, backup_info):
        '''
        Perform the copy of the backup.
        This function returns the size of the backup (in bytes)

        :param backup_info: the backup information structure
        '''

        # paths to be ignored from rsync
        exclude_and_protect = []

        # validate the bandwidth rules against the tablespace list
        tablespaces_bwlimit={}
        if self.config.tablespace_bandwidth_limit and backup_info.tablespaces:
            valid_tablespaces = dict([(tablespace_data[0], tablespace_data[1])
                                     for tablespace_data in backup_info.tablespaces])
            for tablespace, bwlimit in self.config.tablespace_bandwidth_limit.items():
                if tablespace in valid_tablespaces:
                    tablespace_dir = "pg_tblspc/%s" % (valid_tablespaces[tablespace],)
                    tablespaces_bwlimit[tablespace_dir] = bwlimit
                    exclude_and_protect.append(tablespace_dir)

        backup_dest = os.path.join(backup_info.get_basebackup_directory(), 'pgdata')

        # find tablespaces which need to be excluded from rsync command
        if backup_info.tablespaces is not None:
            exclude_and_protect += [
                # removes tablespaces that are located within PGDATA
                # as they are already being copied along with it
                tablespace_data[2][len(backup_info.pgdata):]
                for tablespace_data in backup_info.tablespaces
                if tablespace_data[2].startswith(backup_info.pgdata)
            ]

        rsync = RsyncPgData(ssh=self.server.ssh_command,
                ssh_options=self.server.ssh_options,
                bwlimit=self.config.bandwidth_limit,
                exclude_and_protect=exclude_and_protect,
                network_compression=self.config.network_compression)
        retval = rsync(':%s/' % backup_info.pgdata, backup_dest)
        if retval not in (0, 24):
            msg = "ERROR: data transfer failure"
            _logger.exception(msg)
            raise Exception(msg)

        # deal with tablespaces with a different bwlimit
        if len(tablespaces_bwlimit) > 0:
            for tablespace_dir, bwlimit in tablespaces_bwlimit.items():
                self.current_action = "copying tablespace '%s' with bwlimit %d" % (
                    tablespace_dir, bwlimit)
                _logger.debug(self.current_action)
                tb_rsync = RsyncPgData(ssh=self.server.ssh_command,
                    ssh_options=self.server.ssh_options,
                    bwlimit=bwlimit,
                    network_compression=self.config.network_compression)
                retval = tb_rsync(
                    ':%s/' % os.path.join(backup_info.pgdata, tablespace_dir),
                    os.path.join(backup_dest, tablespace_dir))
                if retval not in (0, 24):
                    msg = "ERROR: data transfer failure on directory '%s'" % (
                        tablespace_dir,)
                    _logger.exception(msg)
                    raise Exception(msg)

        # Copy configuration files (if not inside PGDATA)
        self.current_action = "copying configuration files"
        _logger.debug(self.current_action)
        cf = self.server.get_pg_configuration_files()
        if cf:
            for key in sorted(cf.keys()):
                # Consider only those that reside outside of the original PGDATA
                if cf[key]:
                    if cf[key].find(backup_info.pgdata) == 0:
                        self.current_action = "skipping %s as contained in %s directory" % (key, backup_info.pgdata)
                        _logger.debug(self.current_action)
                        continue
                    else:
                        self.current_action = "copying %s as outside %s directory" % (key, backup_info.pgdata)
                        _logger.info(self.current_action)
                        retval = rsync(':%s' % cf[key], backup_dest)
                        if retval not in (0, 24):
                            raise Exception("ERROR: data transfer failure")

        self.current_action = "calculating backup size"
        _logger.debug(self.current_action)
        backup_size = 0
        for dirpath, _, filenames in os.walk(backup_dest):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                backup_size += os.path.getsize(fp)
        return backup_size

    def backup_stop(self, backup_info):
        '''
        Stop the backup

        :param backup_info: the backup information structure
        '''
        stop_xlog, stop_file_name, stop_file_offset = self.server.pg_stop_backup()
        backup_info.set_attribute("end_time", datetime.datetime.now())
        backup_info.set_attribute("end_xlog", stop_xlog)
        backup_info.set_attribute("end_wal", stop_file_name)
        backup_info.set_attribute("end_offset", stop_file_offset)

    def recover_basebackup_copy(self, backup, dest, remote_command=None):
        '''
        Perform the actual copy of the base backup for recovery purposes

        :param backup: the backup to recover
        :param dest: the destination directory
        :param remote_command: default None. The remote command to recover the base backup,
                               in case of remote backup.
        '''

        sourcedir = os.path.join(backup.get_basebackup_directory(), 'pgdata')
        tablespaces_bwlimit={}
        if remote_command:
            dest = ':%s' % dest

            # validate the bandwidth rules against the tablespace list
            if self.config.tablespace_bandwidth_limit and backup.tablespaces:
                valid_tablespaces = dict([(tablespace_data[0], tablespace_data[1])
                                          for tablespace_data in backup.tablespaces])
                for tablespace, bwlimit in self.config.tablespace_bandwidth_limit.items():
                    if tablespace in valid_tablespaces:
                        tablespace_dir = "pg_tblspc/%s" % (valid_tablespaces[tablespace],)
                        tablespaces_bwlimit[tablespace_dir] = bwlimit

        rsync = RsyncPgData(ssh=remote_command,
                bwlimit=self.config.bandwidth_limit,
                exclude_and_protect=tablespaces_bwlimit.keys(),
                network_compression=self.config.network_compression)
        retval = rsync('%s/' % (sourcedir,), dest)
        if retval != 0:
            raise Exception("ERROR: data transfer failure")

        if remote_command and len(tablespaces_bwlimit) > 0:
            for tablespace_dir, bwlimit in tablespaces_bwlimit.items():
                self.current_action = "copying tablespace '%s' with bwlimit %d" % (
                    tablespace_dir, bwlimit)
                _logger.debug(self.current_action)
                tb_rsync = RsyncPgData(ssh=remote_command,
                                       bwlimit=bwlimit,
                                       network_compression=self.config.network_compression)
                retval = tb_rsync(
                    '%s/' % os.path.join(sourcedir, tablespace_dir),
                    os.path.join(dest, tablespace_dir))
                if retval != 0:
                    msg = "ERROR: data transfer failure on directory '%s'" % (
                        tablespace_dir,)
                    _logger.exception(msg)
                    raise Exception(msg)

        # TODO: Manage different location for configuration files that were not within the data directory

    def recover_xlog_copy(self, compressor, xlogs, wal_dest, remote_command=None):
        """
        Restore WAL segments

        :param compressor: the compressor for the file (if any)
        :param xlogs: the xlog dictionary to recover
        :param wal_dest: the destination directory for xlog recover
        :param remote_command: default None. The remote command to recover the xlog,
                               in case of remote backup.
        """
        rsync = RsyncPgData(ssh=remote_command, bwlimit=self.config.bandwidth_limit,
                            network_compression=self.config.network_compression)
        if remote_command:
            # If remote recovery tell rsync to copy them remotely
            wal_dest = ':%s' % wal_dest
        else:
            # we will not use rsync: destdir must exists
            if not os.path.exists(wal_dest):
                os.makedirs(wal_dest)
        if compressor and remote_command:
            xlog_spool = tempfile.mkdtemp(prefix='barman_xlog-')
        for prefix in xlogs:
            source_dir = os.path.join(self.config.wals_directory, prefix)
            if compressor:
                if remote_command:
                    for segment in xlogs[prefix]:
                        compressor.decompress(os.path.join(source_dir, segment), os.path.join(xlog_spool, segment))
                    rsync.from_file_list(xlogs[prefix], xlog_spool, wal_dest)
                    for segment in xlogs[prefix]:
                        os.unlink(os.path.join(xlog_spool, segment))
                else:
                    # decompress directly to the right place
                    for segment in xlogs[prefix]:
                        compressor.decompress(os.path.join(source_dir, segment), os.path.join(wal_dest, segment))
            else:
                rsync.from_file_list(xlogs[prefix], "%s/" % os.path.join(self.config.wals_directory, prefix), wal_dest)
        if compressor and remote_command:
            shutil.rmtree(xlog_spool)

    def cron_wal_archival(self, compressor, filename):
        """
        Archive a WAL segment from the incoming directory.
        This function returns a WalFileInfo object.

        :param compressor: the compressor for the file (if any)
        :param filename: the name of the WAL file is being processed
        :return WalFileInfo:
        """
        basename = os.path.basename(filename)
        destdir = os.path.join(self.config.wals_directory, xlog.hash_dir(basename))
        destfile = os.path.join(destdir, basename)

        wal_info = WalFileInfo.from_file(filename, compression=None)

        # Run the pre_archive_script if present.
        script = HookScriptRunner(self, 'archive_script', 'pre')
        script.env_from_wal_info(wal_info)
        script.run()

        if not os.path.isdir(destdir):
            os.makedirs(destdir)
        if compressor:
            compressor.compress(filename, destfile)
            shutil.copystat(filename, destfile)
            os.unlink(filename)
        else:
            shutil.move(filename, destfile)

        wal_info = WalFileInfo.from_file(
            destfile,
            compression=compressor and compressor.compression)

        # Run the post_archive_script if present.
        script = HookScriptRunner(self, 'archive_script', 'post')
        script.env_from_wal_info(wal_info)
        script.run()

        return wal_info

    def check(self):
        """
        This function performs some checks on the server.
        Returns 0 if all went well, 1 if any of the checks fails
        """
        if self.config.compression and not self.compression_manager.check():
            output.result('check', self.config.name,
                          'compression settings', False)
        else:
            status = True
            try:
                self.compression_manager.get_compressor()
            except CompressionIncompatibility, field:
                output.result('check', self.config.name,
                              '%s setting' % field, False)
                status = False
            output.result('check', self.config.name,
                          'compression settings', status)

        # Minimum redundancy checks
        no_backups = len(self.get_available_backups())
        if no_backups < self.config.minimum_redundancy:
            status = False
        else:
            status = True
        output.result('check', self.config.name,
                      'minimum redundancy requirements', status,
                      'have %s backups, expected at least %s' %
                      (no_backups, self.config.minimum_redundancy))

    def status(self):
        """
        This function show the server status
        """
        no_backups = len(self.get_available_backups())
        output.result('status', self.config.name,
                      "backups_number",
                      "No. of available backups", no_backups)
        output.result('status', self.config.name,
                      "first_backup",
                      "First available backup",
                      self.get_first_backup())
        output.result('status', self.config.name,
                      "last_backup",
                      "Last available backup",
                      self.get_last_backup())
        if no_backups < self.config.minimum_redundancy:
            output.result('status', self.config.name,
                          "minimum_redundancy",
                          "Minimum redundancy requirements"
                          "FAILED (%s/%s)" % (no_backups,
                                            self.config.minimum_redundancy))
        else:
            output.result('status', self.config.name,
                          "minimum_redundancy",
                          "Minimum redundancy requirements",
                          "satisfied (%s/%s)" % (no_backups,
                          self.config.minimum_redundancy))

    def pg_config_mangle(self, filename, settings, backup_filename=None):
        '''This method modifies the postgres configuration file,
        commenting settings passed as argument, and adding the barman ones.

        If backup_filename is True, it writes on a backup copy.

        :param filename: the Postgres configuration file
        :param settings: settings to mangle dictionary
        :param backup_filename: default False. If True, work on a copy
        '''
        if backup_filename:
            shutil.copy2(filename, backup_filename)

        with open(filename) as f:
            content = f.readlines()

        r = re.compile('^\s*([^\s=]+)\s*=\s*(.*)$')
        mangled = False
        with open(filename, 'w') as f:
            for line in content:
                rm = r.match(line)
                if rm:
                    key = rm.group(1)
                    if key in settings:
                        f.write("#BARMAN# %s" % line)
                        # TODO is it useful to handle none values?
                        f.write("%s = %s\n" % (key, settings[key]))
                        mangled = True
                        continue
                f.write(line)

        return mangled

    def pg_config_detect_possible_issues(self, filename):
        '''This method looks for any possible issue with PostgreSQL
        location options such as data_directory, config_file, etc.
        It returns a dictionary with the dangerous options that have been found.

        :param filename: the Postgres configuration file
        '''

        clashes = {}

        with open(filename) as f:
            content = f.readlines()

        r = re.compile('^\s*([^\s=]+)\s*=\s*(.*)$')
        for line in content:
            rm = r.match(line)
            if rm:
                key = rm.group(1)
                if key in self.DANGEROUS_OPTIONS:
                    clashes[key] = rm.group(2)

        return clashes

    def rebuild_xlogdb(self):
        """
        Rebuild the whole xlog database guessing it from the archive content.
        """
        from os.path import isdir, join

        yield "Rebuilding xlogdb for server %s" % self.config.name
        root = self.config.wals_directory
        default_compression = self.config.compression
        wal_count = label_count = history_count = 0
        # lock the xlogdb as we are about replacing it completely
        with self.server.xlogdb('w') as fxlogdb:
            for name in sorted(os.listdir(root)):
                # ignore the xlogdb and its lockfile
                if name.startswith(self.server.XLOG_DB):
                    continue
                fullname = join(root, name)
                if isdir(fullname):
                    # all relevant files are in subdirectories
                    hash_dir = fullname
                    for wal_name in sorted(os.listdir(hash_dir)):
                        fullname = join(hash_dir, wal_name)
                        if isdir(fullname):
                            _logger.warning(
                                'unexpected directory '
                                'rebuilding the wal database: %s',
                                fullname)
                        else:
                            if xlog.is_wal_file(fullname):
                                wal_count += 1
                            elif xlog.is_backup_file(fullname):
                                label_count += 1
                            else:
                                _logger.warning(
                                    'unexpected file '
                                    'rebuilding the wal database: %s',
                                    fullname)
                                continue
                            wal_info = WalFileInfo.from_file(
                                fullname,
                                default_compression=default_compression)
                            fxlogdb.write(wal_info.to_xlogdb_line())
                else:
                    # only history files are here
                    if xlog.is_history_file(fullname):
                        history_count += 1
                        wal_info = WalFileInfo.from_file(
                            fullname,
                            default_compression=default_compression)
                        fxlogdb.write(wal_info.to_xlogdb_line())
                    else:
                        _logger.warning(
                            'unexpected file '
                            'rebuilding the wal database: %s',
                            fullname)

        yield 'Done rebuilding xlogdb for server %s ' \
            '(history: %s, backup_labels: %s, wal_file: %s)' % (
                self.config.name, history_count, label_count, wal_count)
