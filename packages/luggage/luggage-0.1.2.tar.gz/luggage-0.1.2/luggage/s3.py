from os import makedirs
from os.path import basename, abspath, split, exists
from base64 import b64encode
from urlparse import urlparse

import requests
from dateutil.parser import parse as parsedate

import exceptions
import interface
import parsing.s3 as parsing
import util


class S3Storage(interface.CloudStorage):
    def __init__(self, url, credentials):
        interface.CloudStorage.__init__(self, url.geturl())
        self.bucket = url.netloc
        self.key_id, self.secret_access_key = credentials

        self.session = requests.Session()
        r = self.request('HEAD', '/')

        if r.status_code == 404:
            raise exceptions.ContainerDoesNotExistException('Bucket {0} does not exist'.format(self.bucket))
        elif r.status_code == 403:
            raise exceptions.InvalidCredentialsException('The provided credentials for key {0} '
                                                         'are invalid'.format(self.key_id))
        elif r.status_code != 200:
            raise exceptions.LuggageException.from_respone(r)

    def request(self, verb, path, stream=False, **kwargs):
        url = 'https://{0}.s3.amazonaws.com/{1}'.format(self.bucket, path.lstrip('/'))

        if 'headers' in kwargs:
            kwargs['headers'].update({'Date': util.rfc1123_date()})
        else:
            kwargs['headers'] = {'Date': util.rfc1123_date()}

        request = self.sign_request(requests.Request(verb, url, **kwargs))
        request.stream = True
        return self.session.send(request, stream=stream)

    def sign_request(self, request):
        """
        Prepares and signs a requests.Request

        :param request: The request to sign
        :type request: requests.Request
        :returns: The prepared request, with the Authorization header set
        """
        prepared = request.prepare()
        verb = prepared.method
        content_type = prepared.headers.get('Content-Type', '')
        md5 = ''  # MD5 is optional and caused errors, not using it for now
        # md5 = util.md5(prepared.body)
        date = prepared.headers.get('Date', util.rfc1123_date())
        canonicalized_resource = '/' + self.bucket + urlparse(request.url).path

        canonicalized_headers = ''
        for amz_header in sorted([h for h in request.headers if h.startswith('X-Amz-')]):
            canonicalized_headers += '{0}:{1}\n'.format(amz_header.lower(), request.headers[amz_header])

        to_sign = '{verb}\n' \
                  '{md5}\n' \
                  '{content_type}\n' \
                  '{date}\n' \
                  '{canonicalized_headers}{canonicalized_resource}'.format(**locals())
        print to_sign
        signature = b64encode(util.hmac_sha1(key=self.secret_access_key, to_sign=to_sign))
        prepared.headers['Authorization'] = 'AWS {0}:{1}'.format(self.key_id, signature)
        return prepared

    def _to_info(self, key):
        url = 's3://{0}/{1}'.format(self.bucket, key['name'])
        path = key['name']
        mtime = parsedate(key['last_modified'])
        etag = key['etag']
        size = int(key['size'])
        return interface.ObjectInfo(url, path, mtime, size, etag, {}, self)

    def _infos_from_keys(self, keys):
        return [self._to_info(key) for key in keys]

    def _load_keys(self, path, keys, marker=None):
        headers = {'X-Amz-Prefix': path}
        headers.update({'X-Amz-Marker': marker} if marker is not None else {})

        raw = self.request('GET', '/', headers=headers).text
        response = parsing.parse_bucket_listing(raw)
        keys.extend(self._infos_from_keys(response['contents']))

        return keys, response['truncated'], response.get('next', None)

    def findall(self, path=''):
        # Initial loading
        keys, truncated, marker = self._load_keys(path, keys=[])

        # As long as there is more to load, do it.
        while truncated:
            keys, truncated, marker = self._load_keys(path, keys, marker)

        return keys

    def list(self, path=''):
        return [info.path for info in self.findall(path)]

    def find(self, obj):
        r = self.request('HEAD', '/' + obj)

        if r.status_code == 200:
            url = 's3://{0}/{1}'.format(self.bucket, obj)
            path = obj
            mtime = parsedate(r.headers['Last-Modified'])
            etag = r.headers['ETag'].strip('"')
            size = int(r.headers['Content-Length'])
            return interface.ObjectInfo(url, path, mtime, size, etag, {}, self)
        elif r.status_code == 404:
            raise exceptions.ObjectDoesNotExistException.construct(self.bucket, obj)
        else:
            raise exceptions.LuggageException.from_respone(r)

    def delete(self, obj):
        r = self.request('DELETE', '/' + obj)

        if r.status_code == 204:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise exceptions.LuggageException.from_respone(r)

    def put_file(self, local_file, remote_path=None, verify=False, content_type='application/octet-stream'):
        # TODO: Implement verify switch
        # TODO: Implement adding metadata to the put operation
        # TODO: A TON of other stuff...

        # TODO: Oh, that and the code duplication...
        remote_path = remote_path or basename(local_file)
        r = self.request('PUT', remote_path, data=open(local_file), headers={
            'Content-Type': content_type
        })

        if r.status_code / 100 != 2:
            raise exceptions.LuggageException.from_respone(r)

    def put_data(self, data, remote_path, verify=False, content_type='application/octet-stream'):
        r = self.request('PUT', remote_path, data=data, headers={
            'Content-Type': content_type
        })

        if r.status_code / 100 != 2:
            raise exceptions.LuggageException.from_respone(r)

    def get(self, remote_path, local_file=None):
        if local_file:
            destination = abspath(local_file)
        else:
            destination = abspath(remote_path)

        if '/' in destination:
            destination_directory = split(destination)[0]
            if not exists(destination_directory):
                makedirs(destination_directory)

        r = self.request('GET', remote_path, stream=True)

        if r.status_code == 200:
            with open(destination, 'w+') as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)
            return destination
        else:
            raise exceptions.LuggageException.from_respone(r)

    def read(self, obj, binary=False):
        r = self.request('GET', obj)

        if r.status_code == 200:
            return r.text if binary else r.content
        elif r.status_code == 404:
            raise exceptions.ObjectDoesNotExistException.construct(self.bucket, obj)
        else:
            raise exceptions.LuggageException.from_respone(r)

    def exists(self, obj):
        r = self.request('HEAD', obj)

        if r.status_code / 100 == 2:
            return True
        elif r.status_code == 404:
            return False
        else:
            raise exceptions.LuggageException.from_respone(r)