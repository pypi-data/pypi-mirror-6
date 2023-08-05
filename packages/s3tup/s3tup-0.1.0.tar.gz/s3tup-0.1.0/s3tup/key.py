from binascii import hexlify
import logging
import mimetypes

from bs4 import BeautifulSoup

import s3tup.utils as utils
import s3tup.constants as constants

log = logging.getLogger('s3tup.key')

MULTIPART_CUTOFF = 5242880
MULTIPART_PART_SIZE = 5242880 # Minimum: 5242880

class KeyFactory(object):
    """
    Basically just a container for KeyConfigurators. make_key will create a
    key based on the input parameters and then run each configurator on it
    sequentially, returning a fully configured key.

    """
    def __init__(self, configurators=None):
        self.configurators = configurators or []

    def make_key(self, conn, bucket_name, key_name,):
        """Return a properly configured key"""
        key = Key(conn, bucket_name, key_name)
        return self.configure_key(key)

    def configure_key(self, key):
        for c in self.configurators:
            if c.effects_key(key.name):
                key = c.configure_key(key)
        return key


class KeyConfigurator(object):
    def __init__(self, matcher=None, **kwargs):
        self.matcher = matcher or utils.Matcher()
        for k, v in kwargs.items():
            if k in constants.KEY_ATTRS:
                self.__dict__[k] = v
            else:
                msg = ("__init__() got an unexpected keyword"
                       " argument '{}'".format(k))
                raise TypeError(msg)

    def effects_key(self, key_name):
        """Return whether this configurator effects key_name"""
        return self.matcher.matches(key_name)

    def configure_key(self, key):
        """Return the input key with all configurations applied"""
        for attr in constants.KEY_ATTRS:
            if attr in self.__dict__ and attr != 'metadata':
                key.__dict__[attr] = self.__dict__[attr]
        try: key.metadata.update(self.metadata)
        except AttributeError: pass
        return key

# Both deletion and redirection disregard key configuration,
# so they can be standalone methods.

def delete_key(conn, bucket, key):
    path = key_pretty_path(bucket, key)
    log.info('delete: {}'.format(path))
    conn.make_request('DELETE', bucket, key)

def redirect_key(conn, bucket, key, redirect_url):
    path = key_pretty_path(bucket, key)
    log.info('redirect: {} -> {}'.format(path, redirect_url))
    headers = {'x-amz-website-redirect-location': redirect_url}
    conn.make_request('PUT', bucket, key, headers=headers)

def key_pretty_path(bucket, key):
    return 's3://{}/{}'.format(bucket, key)

class Key(object):
    """
    Encapsulates configuration for a particular s3 key. It has attributes
    (all defined in constants.KEY_ATTRS) that you can set, delete, modify, 
    and then sync to s3 using the sync or upload methods.

    """
    def __init__(self, conn, bucket_name, key_name, **kwargs):
        self.conn = conn
        self.name = key_name
        self.bucket_name = bucket_name

        # Set defaults for required attributes:
        self.reduced_redundancy = kwargs.pop('reduced_redundancy', False)
        self.encrypted = kwargs.pop('encrypted', False)
        self.metadata = kwargs.pop('metadata', {})

        # Add all kwargs passed in that are named in 
        # constants.KEY_ATTRS to this object instance
        for k,v in kwargs.items():
            if k in constants.KEY_ATTRS:
                self.__dict__[k] = v
            else:
                msg = ("__init__() got an unexpected keyword"
                       " argument '{}'".format(k))
                raise TypeError(msg)

    @property
    def pretty_path(self):
        return key_pretty_path(self.bucket_name, self.name)

    def make_request(self, method, params=None, data=None, headers=None):
        """ Convenience method for self.conn.make_request; has bucket and key
            already filled in.
        """
        return self.conn.make_request(
            method,
            self.bucket_name,
            self.name,
            params=params,
            data=data,
            headers=headers
        )

    def get_headers(self):
        """Return the headers associated with this key"""
        headers = {}

        try:
            headers['x-amz-acl'] = self.canned_acl
        except AttributeError:
            pass

        # No need to make separate acl req if acl=None
        try:
            if self.acl is None:
                headers['x-amz-acl'] = 'private'
        except AttributeError:
            pass

        if self.reduced_redundancy:
            headers['x-amz-storage-class'] = 'REDUCED_REDUNDANCY'

        if self.encrypted:
            headers['x-amz-server-side-encryption'] = 'AES256'

        for k, v in self.metadata.items():
            headers['x-amz-meta-' + k] = v

        for k in constants.KEY_HEADERS:
            if k in self.__dict__:
                headers[k.replace('_', '-')] = self.__dict__[k]

        # Guess content-type
        if 'content-type' not in headers:
            content_type_guess = mimetypes.guess_type(self.name)[0]
            if content_type_guess is not None:
                headers['content-type'] = content_type_guess

        return headers

    def delete(self):
        delete_key(self.conn, self.bucket_name, self.name)

    def redirect(self, redirect_url):
        redirect_key(self.conn, self.bucket_name, self.name, redirect_url)

    def sync(self):
        """Sync this object's configuration with its respective key on s3"""
        log.info("sync: {}".format(self.pretty_path))

        headers = self.get_headers()
        headers['x-amz-copy-source'] = '/'+self.bucket_name+'/'+self.name
        headers['x-amz-metadata-directive'] = 'REPLACE'

        # According to S3 docs, copy response can contain error & info
        # even if it returns 200 OK. Need to handle this. However, the
        # docs don't mention what the error would look like...
        self.make_request('PUT', headers=headers)
        self.sync_acl()

    def upload(self, f):
        """Upload file like object to s3 with this key's configuration"""
        try:
            log.info("upload: {} <- {}".format(self.pretty_path, f.name))
        except AttributeError:
            log.info("upload: {}".format(self.pretty_path))

        if utils.f_sizeof(f) <= MULTIPART_CUTOFF:
            self._basic_upload(f)
        else:
            self._multipart_upload(f)
        self.sync_acl()

    def _basic_upload(self, f):
        headers = self.get_headers()
        self.make_request('PUT', headers=headers, data=f)

    def _multipart_upload(self, f):
        upload_id = self._initiate_multipart_upload()

        # Upload individual parts
        upload_reqs = []
        parts = []
        chunks = utils.f_chunk(f, MULTIPART_PART_SIZE)
        for r in range(len(chunks)):
            upload_reqs.append([
                self._multipart_upload_part,
                chunks[r],
                r+1,
                upload_id
            ])
            parts.append((r+1, hexlify(utils.f_md5(chunks[r]))))
        try:
            self.conn.join(upload_reqs)
        except:
            self._abort_multipart_upload(upload_id)
            raise
        
        self._complete_multipart_upload(upload_id, parts)        

    def _initiate_multipart_upload(self):
        headers = self.get_headers()
        resp = self.make_request('POST', 'uploads', headers=headers)
        return BeautifulSoup(resp.text).find('uploadid').text

    def _complete_multipart_upload(self, upload_id, parts):
        data = "<CompleteMultipartUpload>\n"
        for part in parts:
            data += (
                "<Part>\n"
                "  <PartNumber>{}</PartNumber>\n"
                "  <ETag>\"{}\"</ETag>\n"
                "</Part>\n".format(*part)
            )
        data += "</CompleteMultipartUpload>"
        self.make_request('POST', {'uploadId': upload_id}, data=data)

    def _abort_multipart_upload(self, upload_id):
        self.make_request('DELETE', {'uploadId': upload_id})

    def _multipart_upload_part(self, f, part_num, upload_id):
        log.info("upload: {} (part {})".format(self.pretty_path, part_num))
        params = {'partNumber': part_num, 'uploadId': upload_id}
        return self.make_request('PUT', params=params, data=f)

    def sync_acl(self):
        try: acl = self.acl
        except AttributeError: return False
        
        log.info("sync acl: {}".format(self.pretty_path))
        if acl is not None:
            self.make_request('PUT', 'acl', data=acl)