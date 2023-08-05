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

"""Swift helpers."""

__all__ = ['SwiftConnection']

from datetime import datetime, timedelta
import urllib
from uuid import uuid1

from swiftclient import client as swiftclient


class DumbFile(object):
    """Wrap a file-like object just enough for Swift to work around lp:1216981
    """
    def __init__(self, f):
        self._file = f

    def read(self, *args, **kw):
        return self._file.read(*args, **kw)


class SegmentedFile(object):
    """Wrap a file-like object, forcing it to be read in 5GB segments."""
    MAX_SEGMENT_SIZE = 5 * 1024 ** 3  # Swift object size limit - 5GB.

    def __init__(self, f):
        self._file = f
        self._pos = 0
        self.segment = 1
        self.done = False

    def read(self, size=None):
        """Returns EOF if we have reached the segment end, or actual EOF."""
        if self.done:
            return ''

        if self._pos == self.MAX_SEGMENT_SIZE:
            return ''  # End of segment.

        if (size is None or size < 0
            or self._pos + size > self.MAX_SEGMENT_SIZE):
            size = self.MAX_SEGMENT_SIZE - self._pos

        chunk = self._file.read(size)
        chunk_len = len(chunk)

        if chunk_len == 0:
            self.done = True
        else:
            self._pos += chunk_len
            if self._pos > self.MAX_SEGMENT_SIZE:
                # Should never happen.
                raise RuntimeError('Exceeded segment size')

        return chunk

    def next_segment(self):
        """Start the next segment, allowing read() to return more data."""
        self.segment += 1
        self._pos = 0


class SwiftConnection(object):
    '''A simple Swift interface providing just the functionality we need.

    Object names beginning with '...' are reserved for internal use.
    '''

    #: Container used for all operations, automatically created.
    container = None

    #: Chunk size used for all operations that support it.
    chunk_size = 64*1024

    def __init__(self, args):
        self.container = args.container
        self._args = args
        self.reset()

    def reset(self):
        '''Reset the connection.'''
        self._con = swiftclient.Connection(
            authurl=self._args.os_auth_url,
            user=self._args.os_username,
            key=self._args.os_password,
            tenant_name=self._args.os_tenant_name,
            retries=0, auth_version='2.0')
        self._con.put_container(self.container)

    def exists(self, name):
        '''True if the object exists.'''
        try:
            self._con.head_object(self.container, name)
            return True
        except swiftclient.ClientException as x:
            if x.http_status == 404:
                return False
            raise

    def put(self, name, stream, content_type, large=False):
        '''Create an object.

        Overwrites any existing object with the same name.

        Set large to True to upload files larger than 5GB.
        '''
        assert not name.startswith('...'), '{0} is reserved'.format(name)
        if large:
            self._put_large(name, stream, content_type)
        else:
            self._con.put_object(
                self.container, name, DumbFile(stream),
                chunk_size=self.chunk_size, content_type=content_type)

    def _put_large(self, name, stream, content_type):
        '''Upload the stream in 5GB segments.'''

        # We need a UUID to avoid namespace collisions.
        uuid = str(uuid1())

        # Next, create a manifest for the segments we are about to
        # upload under a reserved name. This lets us find segments left
        # around by a failed large object upload and clean them up.
        qcontainer = urllib.quote(self.container, '')
        qname = urllib.quote(name, '')
        quuid = urllib.quote(uuid, '')
        manifest = '{0}/...seg/{1}/{2}/'.format(qcontainer, qname, quuid)
        manifest_headers = {'x-object-manifest': manifest}
        upload_manifest_name = '...uploading/{0}/{1}'.format(qname, quuid)
        self._con.put_object(
            self.container, upload_manifest_name, '', content_length=0,
            content_type=content_type, headers=manifest_headers)

        try:
            # We also use the manifests to detect if a large object with the
            # same name is already being uploaded. We have to do this check
            # after creating the upload-in-progress manifest to avoid race
            # conditions. We must to abort if we detect another upload as
            # we could end up creating a corrupted file. Note that we don't
            # cope with an upload collision between a large object and a
            # normal object, so don't do that.
            existing = self._con.get_container(
                self.container, limit=2,
                prefix='...uploading/{0}/'.format(qname))[1]
            assert len(existing) > 0, 'Lost our upload manifest'
            if len(existing) > 1:
                raise RuntimeError('Upload collision: {0}'.format(name))

            # Trash any existing manifest and segments. Otherwise, we might
            # just overwrite the manifest and leave the segments dangling.
            self.delete(name)

            # Segments need to all be in the same container, have a common
            # object name prefix, and be in ASCII sort order. And of
            # course match the manifest.
            seg_file = SegmentedFile(stream)
            while not seg_file.done:
                # NB. Pad the segment number to ensure correct ASCII order.
                assert seg_file.segment <= 999999
                seg_name = '...seg/{0}/{1}/{2:06}'.format(
                    qname, quuid, seg_file.segment)
                self._con.put_object(
                    self.container, seg_name, seg_file,
                    chunk_size=self.chunk_size,
                    content_type='application/x-swift-segment')
                seg_file.next_segment()

            # Once all the segments are uploaded, create a manifest file
            # to tie them together.
            self._con.put_object(
                self.container, name, '', content_length=0,
                content_type=content_type, headers=manifest_headers)

        except Exception as x:
            # Upload failed. Attempt to delete any objects that actually
            # did get created. This of course may fail, so we still need
            # garbage collection elsewhere.
            try:
                self.reset()
                self.delete(upload_manifest_name)
            except Exception:
                self.reset()
            raise x

        # And delete the upload-in-progress manifest, now we know
        # the upload is complete. This final step might fail, so our
        # garbage collector needs to be smart enough to realize that if
        # there is both an upload-in-progress manifest and a real
        # manifest, the upload actually succeeded and only the
        # upload-in-progress manifest should be removed.
        self._con.delete_object(self.container, upload_manifest_name)


    def get(self, name):
        '''Return a generator yielding the content of the object.'''
        try:
            return self._con.get_object(
                self.container, name, resp_chunk_size=self.chunk_size)[1]
        except swiftclient.ClientException as x:
            if x.http_status == 404:
                return None
            raise

    def delete(self, name):
        '''Delete an object.'''
        try:
            headers = self._con.head_object(self.container, name)
        except swiftclient.ClientException as x:
            if x.http_status == 404:
                return  # Object doesn't exist. Implicit success.
            raise

        manifest = headers.get('x-object-manifest', '')
        if manifest:
            # If we are deleting a manifest, we are deleting a
            # multi-segment large object.
            self._delete_large(name, manifest)
        else:
            self._con.delete_object(self.container, name)

    def _delete_large(self, name, manifest):
        '''
        Delete a multi-segment large object.

        To safely do this:
            1) Create a new manifest under a reserved name, so we don't
               lose track of segments if the deletion is interrupted.
            2) Delete the manifest so nobody accidently tries to use
               a file with missing segments
            3) Delete the segments
            4) Remove the temporary manifest under the reserved name.
        '''
        qname = urllib.quote(name, '')
        # We deliberatly have namespace collisions here, as two
        # simultaneous deletions of the same object are doing the
        # same thing. In addition, if a deletion is interrupted and
        # reissued before garbage collection has run, we don't want
        # to leave a deletion-manifest lying around to cause havoc
        # later. Similarly, an upload explicity deletes the existing
        # object so we don't need to worry about an interrupted deletion
        # destroying uploads.
        deletion_manifest_name = '...to_delete/{0}'.format(qname)
        self._con.put_object(
            self.container, deletion_manifest_name, '', content_length=0,
            headers={'x-object-manifest': manifest})

        # Delete the original manifest. Do this before removing the
        # original segments, or else a client may end up with a partial
        # download and have no way of knowing.
        self._con.delete_object(self.container, name)

        # Delete the segments, wherever they may be.
        container, prefix = (
            urllib.unquote(s) for s in manifest.split('/', 1))
        segs = self._con.get_container(
            container, prefix=prefix, full_listing=True)[1]
        for seg in segs:
            self._con.delete_object(container, seg['name'])

        # Delete the deletion-in-progress manifest.
        self._con.delete_object(container, deletion_manifest_name)

    def list(self, prefix=None):
        '''Full list of objects.

        Returns a sequence of `SwiftObject`s. dictionaries, each
        containing metadata for a single object.
        '''
        return self._con.get_container(
            self.container, prefix=prefix, full_listing=True)[1]

    def size(self, name):
        '''Size of an object.

        The standard 'bytes' item in an object's metadata is not useful
        for large objects (which gives the size of the manifest object - 0).
        '''
        headers = self._con.head_object(self.container, name)

        # If we have a manifest, sum the size of all the segments.
        manifest = headers.get('x-object-manifest', '')
        if manifest:
            container, prefix = (
                urllib.unquote(s) for s in manifest.split('/', 1))
            segs = self._con.get_container(
                container, prefix=prefix, full_listing=True)[1]
            return sum(seg['bytes'] for seg in segs)

        obj = self._con.get_container(
            self.container, prefix=name, limit=1)[1][0]
        return obj['bytes']

    def gc(self, timeout=timedelta(hours=1)):
        '''Delete failed multipart uploads and partial multipart removals.

        If a large object upload or deletion is interrupted, segments will
        be left in Swift that we are required to clean up.

        An upload is deemed failed if there have been no segments created
        over the timeout interval.
        '''
        trashed = []
        # Trash any partially deleted multi-segment objects.
        deletions = self._con.get_container(
            self.container, prefix='...to_delete')[1]
        for obj in deletions:
            self.delete(obj['name'])
            trashed.append(obj['name'])

        # Trash any in-progress uploads that have not had new segments
        # added recently.
        uploads = list(self._con.get_container(
            self.container, prefix='...uploading')[1])
        for upload in uploads:
            # There is a chance the upload was completed fully, except
            # for the final step of removing the upload-in-progress
            # manifest. Extract the object name from the
            # upload-in-process manifest name and use it to see if
            # the completed file was uploaded.
            name = '/'.join(upload['name'].split('/')[1:-1])
            try:
                self._con.head_object(self.container, name)
                self._con.delete_object(self.container, upload['name'])
                continue
            except swiftclient.ClientException as x:
                if x.http_status != 404:
                    raise

            headers = self._con.head_object(self.container, upload['name'])
            manifest = headers.get('x-object-manifest')
            container, prefix = (
                urllib.unquote(s) for s in manifest.split('/', 1))
            segments = self._con.get_container(
                container, prefix=prefix, full_listing=True)[1]
            if segments:
                latest_ts_str = segments[-1]['last_modified']
            else:
                latest_ts_str = upload['last_modified']

            iso_8601_fmt = '%Y-%m-%dT%H:%M:%S.%f'
            last_ts = datetime.strptime(latest_ts_str, iso_8601_fmt)
            now = datetime.utcnow()
            if now > last_ts + timeout:
                self.delete(upload['name'])
                trashed.append(upload['name'])
        return trashed
