import exceptions
import json
from datetime import datetime

import dateutil.parser as dateparser
import requests

import interface


class CloudfilesStorage(interface.CloudStorage):
    AUTH_ENDPOINT = 'https://auth.api.rackspacecloud.com/v1.1/auth'

    def __init__(self, url, credentials):
        interface.CloudStorage.__init__(self, url.geturl())
        self.region = str(url.netloc).upper()
        self.container = str(url.path).strip('/')
        self.mode = url.query.params.get('mode', 'public')
        self.user, self.key = credentials
        self.token = self.endpoint = self.token_expiry = None

    def auth(self):
        if not self.token_expiry or self.token_expiry < datetime.now():
            headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
            payload = {'credentials': { 'username': self.user, 'key': self.key}}
            r = requests.post(self.AUTH_ENDPOINT, headers=headers, data=json.dumps(payload))

            if r.status_code / 100 == 2:
                response = r.json()
                self.token = response['auth']['token']['id']
                self.token_expiry = dateparser.parse(response['auth']['token']['expires'])
                for region in response['auth']['serviceCatalog']['cloudFiles']:
                    if region['region'] == self.region:
                        self.endpoint = region[self.mode + 'URL'].replace('\\', '')
                        break
                else:
                    raise Exception('Unknown region: {}'.format(self.region))
            else:
                # TODO: More detailed error message
                raise exceptions.InvalidCredentialsException('Auth against rackspace failed')

    def container_url(self):
        return self.endpoint + '/' + self.container

    def object_url(self, obj):
        return self.container_url() + '/' + obj

    def request(self, method, url, **kwargs):
        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers']['X-Auth-Token'] = self.token
        return requests.request(method, url, **kwargs)

    def ls(self, path=''):
        self.auth()
        r = self.request('GET', self.container_url())

        object_count = int(r.headers['X-Container-Object-Count'])
        grepped = (r.text.split('\n')[:-1])  # Take away trailing newline

        while len(grepped) < object_count:
            r = self.request('GET', self.container_url(), params={'marker': grepped[-1]})
            grepped += (r.text.split('\n')[:-1])
            object_count = int(r.headers['X-Container-Object-Count'])

        return grepped
