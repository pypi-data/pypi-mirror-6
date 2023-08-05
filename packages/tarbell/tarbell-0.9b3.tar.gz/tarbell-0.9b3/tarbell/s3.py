import gzip
import mimetypes
import os
import os.path
import re
import shutil
import tempfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from clint.textui import puts
from urllib import quote_plus
from urllib2 import urlopen

excludes = r'|'.join([r'.*\.git$'])


class S3Url(str):
    def __new__(self, content):
        # Parse
        if not content.endswith("/"):
            content = "{0}/".format(content)
        if content.startswith("s3://"):
            content = content[5:]
        self.root, self.path = content.split("/", 1)
        return str.__new__(self, content.rstrip("/"))


class S3Sync:
    def __init__(self, directory, bucket, access_key_id, secret_access_key, force=False):
        connection = S3Connection(access_key_id, secret_access_key)
        self.force = force
        self.bucket = bucket
        self.connection = connection.get_bucket(bucket.root)
        self.directory = directory.rstrip('/')

    def deploy_to_s3(self):
        """
        Deploy a directory to an s3 bucket.
        """
        self.tempdir = tempfile.mkdtemp('s3deploy')

        for keyname, absolute_path in self.find_file_paths():
            self.s3_upload(keyname, absolute_path)

        shutil.rmtree(self.tempdir, True)
        return True

    def s3_upload(self, keyname, absolute_path):
        """
        Upload a file to s3
        """
        mimetype = mimetypes.guess_type(absolute_path)
        options = {'Content-Type': mimetype[0]}

        if mimetype[0] is not None and mimetype[0].startswith('text/'):
            upload = open(absolute_path)
            options['Content-Encoding'] = 'gzip'
            key_parts = keyname.split('/')
            filename = key_parts.pop()
            temp_path = os.path.join(self.tempdir, filename)
            gzfile = gzip.open(temp_path, 'wb')
            gzfile.write(upload.read())
            gzfile.close()
            absolute_path = temp_path

        size = os.path.getsize(absolute_path)
        key = "{0}/{1}".format(self.bucket.path, keyname)
        existing = self.connection.get_key(key)

        if self.force or not existing or (existing.size != size):
            k = Key(self.connection)
            k.key = key
            puts("+ Uploading {0}/{1}".format(self.bucket, keyname))
            k.set_contents_from_filename(absolute_path, options, policy='public-read')
        else:
            puts("- Skipping  {0}/{1}, file sizes match".format(self.bucket, keyname))


    def find_file_paths(self):
        """
        A generator function that recursively finds all files in the upload directory.
        """
        paths = []
        for root, dirs, files in os.walk(self.directory, topdown=True):
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]
            rel_path = os.path.relpath(root, self.directory)

            for f in files:
                if f.startswith('.'):
                    continue
                if rel_path == '.':
                    paths.append((f, os.path.join(root, f)))
                else:
                    paths.append((os.path.join(rel_path, f), os.path.join(root, f)))

        return paths
