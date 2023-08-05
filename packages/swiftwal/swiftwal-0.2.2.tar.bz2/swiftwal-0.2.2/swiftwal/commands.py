# This file is part of SwiftWAL, a tool to integrate PostgreSQL
# filesystem level backups, WAL archiving and point-in-time recovery
# with OpenStack Swift storage.
# Copyright 2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Command line interface."""

__all__ = []

import argparse
import ConfigParser
from cStringIO import StringIO
from datetime import datetime
import os.path
import re
import subprocess
import sys
from tempfile import NamedTemporaryFile
import time

import swiftwal
from swiftwal.swiftconnection import SwiftConnection


def fatal(msg):
    '''Emit an error message and exit with a failure code.'''
    sys.stderr.write('FATAL: {0}\n'.format(msg))
    raise SystemExit(1)


def warn(msg):
    '''Emit a warning message.'''
    sys.stderr.write('WARNING: {0}\n'.format(msg))


def info(msg):
    '''Emit an informative message.'''
    sys.stderr.write('INFO: {0}\n'.format(msg))


def check_process(*procs):
    '''Confirm processes have not yet failed.

    Used as an attempt to catch subprocesses failures early.
    '''
    for proc in procs:
        rc = proc.poll()
        if not (rc is None or rc == 0):
            raise SystemExit(rc)


def psize(size):
    units = ['B  ', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return "{0:.4g} {1}".format(float(size), unit)
        size = size / 1024.0


def prate(start_time, end_time, size):
    ps = psize(float(size) / (end_time - start_time))
    if ps.endswith('B'):
        return '{0}/s'.format(ps)
    else:
        return '{0} B/s '.format(ps.rtrim())


def list_backups(swift):
    '''List stored backups in order.

    Returns a sequence of (timestamp, obj_name, obj_size).
    '''
    objs = sorted(swift.list(prefix='pg_basebackup_'), key=lambda x: x['name'])
    backups = []
    for obj in objs:
        obj_name = obj['name']
        match = re.search(r'^pg_basebackup_(\d{8}T\d{4}Z)\.tgz$', obj_name)
        if match is None:
            continue
        timestamp = match.group(1)
        backups.append((timestamp, obj_name))
    return backups


def list_wals(swift):
    '''List stored WAL files in order.

    This not only includes the 16MB WAL segments, but also .history file.

    Returns a sequence of (name, obj_name, obj_size).
    '''
    objs = sorted(swift.list(prefix='wal_'), key=lambda x: x['name'])
    wals = []
    for obj in objs:
        obj_name = obj['name']
        obj_size = obj['bytes']
        match = re.search(r'^wal_(.+).gz$', obj_name)
        if match is None:
            warn('Skipping unknown object {0}'.format(obj_name))
            continue
        name = match.group(1)
        wals.append((name, obj_name, obj_size))
    return wals


def backup_obj_name(timestamp):
    '''The Swift object name for a backup identified by timestamp.'''
    return 'pg_basebackup_{0}.tgz'.format(timestamp)


def label_obj_name(timestamp):
    '''The Swift object name for a backup label identified by timestamp.'''
    return 'backup_label_{0}.txt'.format(timestamp)


def wal_obj_name(name):
    '''The Swift object name for a WAL file identified by name.'''
    return 'wal_{0}.gz'.format(name)


def backup_label(swift, timestamp):
    '''Retrieve the backup_label for the backup.'''
    obj_name = label_obj_name(timestamp)
    content = swift.get(obj_name)
    if content is None:
        # If we get here, then we managed to store a backup but not the
        # label to go with it. Repair the situation, rather than ignore
        # a potentially valuable backup.
        return _create_backup_label(swift, timestamp)
    return ''.join(content)


def _create_backup_label(swift, timestamp):
    '''Extract the backup_label from the tarball.

    The label is always at the start of the tarball, so only the
    first bit of the file is actually downloaded.
    '''
    obj_name = backup_obj_name(timestamp)
    content = swift.get(obj_name)
    if content is None:
        fatal('Backup {0} not found'.format(obj_name))
    label = None
    with NamedTemporaryFile() as temp_file:
        extract_label_proc = subprocess.Popen(
            ['tar', '--extract', '--gzip', '--to-stdout', 'backup_label'],
            stdin=subprocess.PIPE, stdout=temp_file, stderr=subprocess.PIPE)
        for chunk in content:
            extract_label_proc.stdin.write(chunk)
            if extract_label_proc.poll() is not None:
                fatal('tar completed with {0}\n{1}'.format(
                    extract_label_proc.returncode,
                    extract_label_proc.stderr.read()))
            if os.path.getsize(temp_file.name) > 0:
                label = open(temp_file.name, 'r').read()
                # Last time is the LABEL and terminating newline.
                # If we find this, the label has been fully
                # extracted.
                match = re.search(r'\nLABEL:\s.+\n$', label)
                if match is not None:
                    extract_label_proc.kill()
                    break
    swift.reset()  # Terminate the partial download

    if label is None:
        fatal('No backup_label found in {0}'.format(obj_name))

    swift.put(label_obj_name(timestamp), StringIO(label), 'text/plain')

    return label


def backup_command(args):
    '''Handle the db-backup command.'''
    start_time = time.time()
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%MZ')
    print 'Creating backup {0} in container {1}'.format(
        timestamp, args.container)

    obj_name = backup_obj_name(timestamp)

    backup_cmd = [
        'pg_basebackup',
        '--format=tar',
        '--pgdata=-',
        '--no-password',
        '--checkpoint={0}'.format(args.checkpoint),
        '--label={0}'.format(args.label),
        ]
    if args.verbose:
        backup_cmd.append('--verbose')
    if args.xlog:
        backup_cmd.append('--xlog')
    if args.progress:
        backup_cmd.append('--progress')
    if args.pg_user:
        backup_cmd.extend(['-U', args.pg_user])
    if args.pg_host:
        backup_cmd.extend(['-h', args.pg_host])
    if args.pg_port:
        backup_cmd.extend(['-p', args.pg_port])

    compress_cmd = ['pigz', '--to-stdout']

    backup_proc = subprocess.Popen(
        backup_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    backup_proc.stdin.close()

    compress_proc = subprocess.Popen(
        compress_cmd, stdin=backup_proc.stdout, stdout=subprocess.PIPE)

    backup_proc.stdout.close()  # Allow correct SIGPIPE propagation.

    swift = SwiftConnection(args)

    check_process(backup_proc, compress_proc)

    swift.put(
        obj_name, compress_proc.stdout,
        'application/x-gtar-compressed', large=True)

    if backup_proc.wait() != 0:
        fatal("Backup failed")
    if compress_proc.wait() != 0:
        fatal("Compression failed")

    label = _create_backup_label(swift, timestamp)
    if args.verbose:
        print label


def restore_command(args):
    '''Handle the db-restore command.'''
    args.timestamp = args.timestamp.upper()
    if not args.timestamp.endswith('Z'):
        args.timestamp += 'Z'
    try:
        datetime.strptime(args.timestamp, '%Y%m%dT%H%MZ')
    except ValueError:
        fatal('Timestamp {0} does not match %Y%m%dT%H%MZ'.format(
            args.timestamp))

    if os.path.exists(args.dir):
        if os.path.isdir(args.dir):
            if os.listdir(args.dir):
                fatal('{0} is not empty'.format(args.dir))
        else:
            fatal('{0} already exists'.format(args.dir))
    else:
        os.makedirs(args.dir, 0o700)

    decompress_cmd = ['pigz', '--decompress', '--to-stdout']
    untar_cmd = ['tar', '--extract', '--directory', args.dir, '--totals']
    if args.verbose:
        untar_cmd.append('--verbose')

    decompress_proc = subprocess.Popen(
        decompress_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    untar_proc = subprocess.Popen(untar_cmd, stdin=decompress_proc.stdout)
    decompress_proc.stdout.close()  # Allow correct SIGPIPE propagation.

    check_process(decompress_proc, untar_proc)

    swift = SwiftConnection(args)
    obj_name = backup_obj_name(args.timestamp)
    content = swift.get(obj_name)

    if content is None:
        fatal('Backup {0} does not exist in container {1}'.format(
            obj_name, args.container))

    for chunk in content:
        decompress_proc.stdin.write(chunk)
    decompress_proc.stdin.close()

    if decompress_proc.wait() != 0:
        fatal('Failed to decompress {0} from container {1}'.format(
            obj_name, args.container))

    if untar_proc.wait() != 0:
        fatal('Failed to untar {0} from container {1}'.format(
            obj_name, args.container))


def list_backups_command(args):
    '''Handle the list command.'''
    swift = SwiftConnection(args)
    if args.verbose:
        print "Size     \tTimestamp     \tSwift Object Name"
        print "=========\t==============\t================================"
        total_size = 0
        for timestamp, obj_name in list_backups(swift):
            obj_size = swift.size(obj_name)
            total_size = total_size + obj_size
            print "{0}\t{1}\t{2}".format(psize(obj_size), timestamp, obj_name)
        print
        print "Total Size: {0}".format(psize(total_size))
    else:
        for timestamp, obj_name in list_backups(swift):
            print timestamp


def label_command(args):
    '''Handle the label command.'''
    swift = SwiftConnection(args)
    sys.stdout.write(backup_label(swift, args.timestamp))


def archive_wal_command(args):
    '''Handle the wal-archive command.'''
    start_time = time.time()
    swift = SwiftConnection(args)

    wal_path = args.wal_path
    wal_name = os.path.basename(wal_path)

    # Sanity check the WAL file. Not much to do here - usually it will
    # be a 16MB WAL file, but it might be a .backup or .history file.
    if not os.path.exists(wal_path):
        fatal('WAL {0} does not exist'.format(wal_path))

    if not os.path.isfile(wal_path):
        fatal('{0} is not a standard file'.format(wal_path))

    wal_size = os.path.getsize(wal_path)

    obj_name = wal_obj_name(wal_name)

    # Fail if WAL file already exists to avoid accidental dataloss if
    # misconfiguration caused two databases to log to the same
    # container, per PostgreSQL continuous archiving docs. These checks
    # are always racy, but better than nothing.
    if swift.exists(obj_name):
        msg = 'WAL {0} already exists in Swift container {1}'.format(
            wal_name, args.container)
        if args.force:
            warn(msg + '. Overwriting.')
        else:
            fatal(msg)

    print 'Archiving WAL {0} to container {1}'.format(wal_path, args.container)
    compress_cmd = ['pigz', '--to-stdout']

    compress_proc = subprocess.Popen(
        compress_cmd, stdin=open(wal_path, 'rb'), stdout=subprocess.PIPE)

    check_process(compress_proc)

    swift.put(
        obj_name, compress_proc.stdout,
        'application/x-postgresql-wal-compressed')

    if compress_proc.wait() != 0:
        fatal("Compression failed")

    if args.verbose:
        info('Archived WAL {0} to container {1} at {2}'.format(
            wal_path, args.container,
            prate(start_time, time.time(), wal_size)))


def restore_wal_command(args):
    '''Handle the restore-wal command.'''
    start_time = time.time()
    swift = SwiftConnection(args)

    wal_name = args.wal_name
    wal_path = args.wal_path

    if os.path.isdir(wal_path):
        wal_path = os.path.join(wal_path, wal_name)

    obj_name = wal_obj_name(wal_name)

    content = swift.get(obj_name)
    if content is None:
        # This command is designed to be used as a recovery_command,
        # so file not found is expected and not an error. Just print
        # an informative and non-scary message and return a non-zero
        # exit code.
        info('WAL {0} not found in Swift container {1}'.format(
            wal_name, args.container))
        sys.exit(1)

    decompress_cmd = ['pigz', '--decompress', '--to-stdout']
    decompress_proc = subprocess.Popen(
        decompress_cmd, stdin=subprocess.PIPE, stdout=open(wal_path, 'wb'))
    check_process(decompress_proc)

    for chunk in content:
        decompress_proc.stdin.write(chunk)
    decompress_proc.stdin.close()

    if decompress_proc.wait() != 0:
        fatal('Failed to decompress {0}'.format(obj_name))

    if args.verbose:
        wal_size = os.path.getsize(wal_path)
        info('Restored WAL {0} to {1} at {2}'.format(
            wal_name, wal_path,
            prate(start_time, time.time(), wal_size)))

def archive_cleanup_command(args):
    '''Handle the archive-cleanup command.'''
    restart_wal_name = args.restart_wal_name

    # Per pg_archivecleanup behavior, if a .backup file has been
    # specified then only the file prefix will be used as the
    # restart_wal_name. In particular, if passed
    # '123456781234567812345678.12345678.backup',
    # we don't want to destroy '123456781234567812345678'.
    if len(restart_wal_name) == 40 and restart_wal_name.endswith('.backup'):
        restart_wal_name = restart_wal_name.split('.', 1)[0]

    # Abort if sanity check fails.
    if len(restart_wal_name) != 24:
        fatal("Invalid restart wal file name {0!r}".format(restart_wal_name))
    try:
        int(restart_wal_name, 16)
    except ValueError:
        fatal("Invalid restart wal file name {0!r}".format(restart_wal_name))

    info("Keep WAL file {0!r} and later".format(restart_wal_name))

    swift = SwiftConnection(args)

    for wal_name, obj_name, _ in list(list_wals(swift)):
        # Per pg_archivecleanup.c in the PostgreSQL source, we ignore
        # the timeline part of the WAL file name to ensure we won't
        # prematurely remove a segment from a parent timeline.
        if wal_name[8:] >= restart_wal_name[8:]:
            continue
        info("Removing WAL file {0!r}".format(wal_name))
        if not args.dry_run:
            swift.delete(obj_name)


def list_wal_command(args):
    '''Handle the wal-list command.'''
    swift = SwiftConnection(args)
    if args.verbose:
        print "Size     \tName"
        print "=========\t========================"
        total_size = 0
        for name, _, obj_size in list_wals(swift):
            total_size = total_size + obj_size
            print "{0:>9}\t{1}".format(psize(obj_size), name)
        print
        print "Total Size: {0}".format(psize(total_size))
    else:
        for name, _, obj_size in list_wals(swift):
            print name


def prune_command(args):
    '''Handle the prune command.'''
    swift = SwiftConnection(args)

    if args.keep_backups < 0:
        fatal("Invalid value for --keep-backups ({0})".format(
            args.keep_backups))

    if args.keep_backups < 0:
        fatal("Invalid value for --keep-wal ({0})".format(
            args.keep_wals))

    trashed = swift.gc()
    for name in trashed:
        warn('Garbage collected {0}'.format(name))

    backups = list_backups(swift)
    backups_to_delete = backups[:-args.keep_backups]
    backups_to_keep = backups[-args.keep_backups:]

    # Identify the first WAL file we need to keep for the oldest
    # backup we are keeping. All WAL information before this may
    # be removed.
    backup_label_content = backup_label(swift, backups_to_keep[0][0])
    match = re.search(
        r'^START WAL LOCATION: .* \(file ([^\s]+)\)$',
        backup_label_content, re.M)
    if match is None:
        fatal("Invalid backup_label {0}".format(backups_to_keep[0][0]))
    first_needed_wal = match.group(1)

    # Keep at least args.keep_wals files, and everything required for
    # PITR of the oldest backup.
    wals = list_wals(swift)
    wals_to_keep = wals[-args.keep_wals:]
    wals_to_delete = []
    for wal in wals[:-args.keep_wals]:
        if wal[0] < first_needed_wal:
            wals_to_delete.append(wal)
        else:
            wals_to_keep.append(wal)

    # Output what we are about to do.
    if backups_to_delete:
        print 'Removing {0:>4} backups,   {1} -> {2}'.format(
            len(backups_to_delete),
            backups_to_delete[0][0],
            backups_to_delete[-1][0])
    else:
        print 'Removing    0 backups.'

    if backups_to_keep:
        print 'Keeping  {0:>4} backups,   {1} -> {2}'.format(
            len(backups_to_keep),
            backups_to_keep[0][0],
            backups_to_keep[-1][0])
    else:
        print 'Keeping    0 backups.'

    if args.verbose:
        for timestamp, obj_name in backups:
            print ' '*24,
            if (timestamp, obj_name) in backups_to_delete:
                print '{0} (REMOVING)'.format(timestamp)
            else:
                print timestamp

    print

    if wals_to_delete:
        print 'Removing {0:>4} WAL files, {1} -> {2}'.format(
            len(wals_to_delete),
            wals_to_delete[0][0],
            wals_to_delete[-1][0])
    else:
        print 'Removing    0 WAL files.'

    if wals_to_keep:
        print 'Keeping  {0:>4} WAL files, {1} -> {2}'.format(
            len(wals_to_keep),
            wals_to_keep[0][0],
            wals_to_keep[-1][0])
    else:
        print 'Keeping    0 WAL files.'

    if args.verbose:
        for name, obj_name, obj_size in wals:
            print ' '*24,
            if (name, obj_name, obj_size) in wals_to_delete:
                print '{0} (REMOVING)'.format(name)
            else:
                print name

    print

    total_removed_size = 0
    for timestamp, obj_name in backups_to_delete:
        obj_size = swift.size(obj_name)
        total_removed_size = total_removed_size + obj_size
        if args.verbose:
            print 'Backup {0}'.format(timestamp),
        if not args.dry_run:
            swift.delete(obj_name)
        if args.verbose:
            print '(GONE)'

    for name, obj_name, obj_size in wals_to_delete:
        total_removed_size = total_removed_size + obj_size
        if args.verbose:
            print 'WAL {0}'.format(name),
        if not args.dry_run:
            swift.delete(obj_name)
        if args.verbose:
            print '(GONE)'

    print
    print 'Removed {0}'.format(psize(total_removed_size))


class SimpleConfig:
    '''Simple key=value config file parser.'''
    def __init__(self, parser, args):
        self._config = ConfigParser.RawConfigParser(os.environ)
        if args.config:
            if os.path.exists(args.config):
                config_file = StringIO(
                    '[DEFAULT]\n' + open(args.config).read())
                self._config.readfp(config_file, args.config)
            else:
                parser.error('Config file {0} does not exist'.format(
                    args.config))

    def __getitem__(self, key):
        try:
            return self._config.get('DEFAULT', key)
        except ConfigParser.NoOptionError:
            return None


def main():
    '''Parse the command line and do the requested operation.'''
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--version', action='version',
        version='%(prog)s {0}'.format(swiftwal.__version__))

    parser.add_argument(
        '--config', '-c', metavar='FILE',
        help="SwiftWAL configuration file")

    parser.add_argument(
        '--os-auth-url', metavar='URL',
        help='OpenStack authentication URL. Defaults to $OS_AUTH_URL.')
    parser.add_argument(
        '--os-username', metavar='USER',
        help='OpenStack username. Defaults to $OS_USERNAME.')
    parser.add_argument(
        '--os-password', metavar='KEY',
        help='OpenStack key. Defaults to $OS_PASSWORD.')
    parser.add_argument(
        '--os-tenant-name', metavar='TENANT',
        help='OpenStack tenant name. Defaults to $OS_TENANT_NAME')
    parser.add_argument(
        '--container', '-C', metavar='CONTAINER',
        help='container to store data in')
    parser.add_argument(
        '--verbose', '-v', action="store_true", default=False,
        help="extra output")

    subparsers = parser.add_subparsers()

    backup_parser = subparsers.add_parser('backup')
    backup_parser.add_argument(
        '-x', '--xlog', action='store_true', default=False,
        help='include required WAL files in backup')
    backup_parser.add_argument(
        '-c', '--checkpoint', choices=['fast', 'spread'], default='spread',
        help='Sets checkpoint mode to fast or spread.')
    backup_parser.add_argument(
        '-P', '--progress', action='store_true', dest='progress',
        help='show progress information', default=False)
    backup_parser.add_argument(
        '-l', '--label', dest='label', metavar='LABEL',
        default='pg_basebackup (via SwiftWAL)', help='set backup label')
    backup_parser.add_argument(
        '-U', '--username', dest='pg_user', metavar='NAME',
        help='connect as PostgreSQL user NAME')
    backup_parser.add_argument(
        '-H', '--host', dest='pg_host', metavar='HOSTNAME',
        help='host PostgreSQL is running on')
    backup_parser.add_argument(
        '-p', '--port', dest='pg_port', metavar='PORT',
        help='port number PostgreSQL is listening on')
    backup_parser.set_defaults(func=backup_command)

    restore_parser = subparsers.add_parser('restore')
    restore_parser.add_argument(
        'timestamp', metavar='<YYYYmmdd>T<HHMM>Z',
        help='timestamp of database backup to restore')
    restore_parser.add_argument(
        'dir', metavar='DIR',
        help='restore to DIR. Must be empty or non-existant.')
    restore_parser.set_defaults(func=restore_command)

    list_parser = subparsers.add_parser('list-backups')
    list_parser.set_defaults(func=list_backups_command)

    label_parser = subparsers.add_parser('label')
    label_parser.add_argument(
        'timestamp', metavar='<YYYYmmdd>T<HHMM>Z',
        help='display backup_label of a backup')
    label_parser.set_defaults(func=label_command)

    archive_wal_parser = subparsers.add_parser('archive-wal')
    archive_wal_parser.add_argument(
        '--force', '-f', action='store_true', default=False,
        help='Force upload even if WAL file already exists in Swift')
    archive_wal_parser.add_argument(
        'wal_path', metavar='WAL',
        help='path to WAL file to archive')
    archive_wal_parser.set_defaults(func=archive_wal_command)

    restore_wal_parser = subparsers.add_parser('restore-wal')
    restore_wal_parser.add_argument(
        'wal_name', metavar='WAL', help='WAL name to restore')
    restore_wal_parser.add_argument(
        'wal_path', metavar='PATH', help='path to restore WAL to')
    restore_wal_parser.set_defaults(func=restore_wal_command)

    list_wal_parser = subparsers.add_parser('list-wal')
    list_wal_parser.set_defaults(func=list_wal_command)

    archive_cleanup_parser = subparsers.add_parser('archive-cleanup')
    archive_cleanup_parser.add_argument(
        'restart_wal_name', metavar='RLOC',
        help='Remove all WAL files preceding RLOC. See pg_archivecleanup(1).')
    archive_cleanup_parser.add_argument(
        '-n', '--dry-run', action="store_true", default=False,
        help="don't actually delete anything.")
    archive_cleanup_parser.set_defaults(func=archive_cleanup_command)

    prune_parser = subparsers.add_parser('prune')
    prune_parser.add_argument(
        '--keep-backups', type=int, required=True, metavar='N',
        help='delete all backups except the last N')
    prune_parser.add_argument(
        '--keep-wals', type=int, required=True, metavar='N',
        help='delete all WAL files except the last N unless required for PITR')
    prune_parser.add_argument(
        '-n', '--dry-run', action="store_true", default=False,
        help="don't actually delete anything.")

    prune_parser.set_defaults(func=prune_command)

    args = parser.parse_args()

    config = SimpleConfig(parser, args)

    args.os_auth_url = (
        args.os_auth_url or config['OS_AUTH_URL']
        or parser.error('OS_AUTH_URL is required'))

    args.os_username = (
        args.os_username or config['OS_USERNAME']
        or parser.error('OS_USERNAME is required'))

    args.os_password = (
        args.os_password or config['OS_PASSWORD']
        or parser.error('OS_PASSWORD is required'))

    args.os_tenant_name = (
        args.os_tenant_name or config['OS_TENANT_NAME']
        or parser.error('OS_TENANT_NAME is required'))

    args.container = (
        args.container or config['CONTAINER']
        or parser.error('CONTAINER is required'))

    args.func(args)


if __name__ == '__main__':
    main()
