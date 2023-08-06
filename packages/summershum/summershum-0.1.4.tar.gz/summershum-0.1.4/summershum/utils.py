import hashlib
import os
import zipfile

import requests

from subprocess import Popen, PIPE

from kitchen.text.converters import to_unicode
from model import File

import logging
log = logging.getLogger("summershum")


def download_lookaside(message, lookaside_url, tmpdir):
    """ For a provided pkg updated, download the sources. """

    url = '%(base_url)s/%(pkg_name)s/%(sources)s/%(md5)s/%(sources)s' % (
        {
            'base_url': lookaside_url, 'pkg_name': message['name'],
            'sources': message['filename'], 'md5': message['md5sum']
        }
    )

    local_filename = "/".join([tmpdir, message['filename']])

    req = requests.get(url, stream=True)
    with open(local_filename, 'wb') as stream:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                stream.write(chunk)
                stream.flush()


def calculate_sums(session, message, tmpdir):
    """ Extract the content of the file extracted from the fedmsg message
    and browse the sources of the specified package and for each of the
    files in the sources get their sha256sum, sha1sum, and md5sum.
    """

    local_filename = "/".join([tmpdir, message['filename']])

    if not os.path.exists(local_filename):
        raise IOError('File %s not found' % local_filename)

    # FIXME: support gems
    if local_filename.endswith('.gem'):
        return

    if zipfile.is_zipfile(local_filename):
        if local_filename.endswith('.jar') or local_filename.endswith('.war'):
            log.warning('Invalid sources uploaded: %r - package: %r' % (
                local_filename, message.get('name')))
            return

    cmd = ['rpmdev-extract', '-C', tmpdir, local_filename]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    if proc.returncode:
        raise IOError(
            'Something went wrong when extracting %s' % local_filename)

    filename = proc.communicate()[0].split('\n')[0].split('/')[0]

    if filename:
        filename = "/".join([tmpdir, filename])
    else:
        log.warning("No files extracted from %r" % local_filename)
        filename = tmpdir

    count, stored = 0, 0
    for fname, sha256sum, sha1sum, md5sum in walk_directory(filename):
        count = count + 1
        pkgobj = File.exists(session, message['md5sum'], fname)
        fname = fname.replace(tmpdir, '')
        if not pkgobj:
            pkgobj = File(
                pkg_name=message['name'],
                filename=fname,
                sha256sum=sha256sum,
                sha1sum=sha1sum,
                md5sum=md5sum,
                tar_file=message['filename'],
                tar_sum=message['md5sum']
            )
            session.add(pkgobj)
            stored = stored + 1
        else:
            pass
    session.commit()

    if local_filename and os.path.exists(local_filename):
        os.unlink(local_filename)

    log.info("Stored %i of %i files" % (stored, count))


def walk_directory(directory):
    """ Return a tuple (filename, sha256, sha1, md5) for every files present in
    the specified folder and do so recursively.
    """
    for root, dirnames, filenames in os.walk(directory):

        for filename in filenames:
            file_path = os.path.join(root, filename)

            # We skip the symlink, should we follow them instead?
            if os.path.islink(file_path):
                log.warning("File %r is a link - skipping", file_path)
                continue

            with open(file_path) as stream:
                contents = stream.read()
                sha256sum = hashlib.sha256(contents).hexdigest()
                sha1sum = hashlib.sha1(contents).hexdigest()
                md5sum = hashlib.md5(contents).hexdigest()
                yield (to_unicode(file_path), sha256sum, sha1sum, md5sum)
