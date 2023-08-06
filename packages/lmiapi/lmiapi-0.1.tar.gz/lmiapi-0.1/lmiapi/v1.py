# Python
import json
import logging
import os
import urlparse

# Requests
import requests
from requests.structures import CaseInsensitiveDict

__all__ = ['LogMeInAPI']

logger = logging.getLogger('lmiapi.v1')


class LogMeInAPI(object):

    API_ROOT = 'https://secure.logmein.com/public-api/v1/'

    def __init__(self, creds):
        self.creds = self._check_creds(creds)
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/JSON'})
        self.session.headers.update({'Authorization': json.dumps(self.creds)})

    def _check_creds(self, creds):
        d = CaseInsensitiveDict()
        if isinstance(creds, dict):
            d.update(creds)
        elif isinstance(creds, basestring):
            if os.path.exists(creds):
                creds = file(creds, 'r').read()
            for line in creds.splitlines():
                if ':' in line:
                    k,v = line.split(':', 1)
                    d[k.strip()] = v.strip()
        else:
            raise TypeError('unsupported type for credentials data')
        if 'companyId' not in d and 'CID' in d:
            d['companyId'] = d['CID']
        if 'companyId' in d and not 'psk' in d:
            raise ValueError('psk is required when companyId is provided')
        elif 'psk' in d and not 'companyId' in d:
            raise ValueError('companyId is required when psk is provided')
        elif 'companyId' in d and 'psk' in d:
            return {
                'companyId': int(d['companyId']),
                'psk': str(d['psk']),
            }
        elif 'loginSessionId' in d and not 'profileId' in d:
            raise ValueError('profileId is required when loginSessionId is '
                             'provided')
        elif 'profileId' in d and not 'loginSessionId' in d:
            raise ValueError('loginSessionId is required when profileId is '
                             'provided')
        elif 'loginSessionId' in d and 'profileId' in d:
            return {
                'loginSessionId': str(d['loginSessionId']),
                'profileId': int(d['profileId']),
            }
        else:
            raise ValueError('either companyId+psk or '
                             'loginSessionId+profileId must be provided')

    def _get(self, path):
        url = '%s%s' % (self.API_ROOT, path.lstrip('/'))
        response = self.session.get(url)
        #logger.debug('GET %s -> %d', url, response.status_code)
        return response.json()

    def _post(self, path, data):
        url = '%s%s' % (self.API_ROOT, path.lstrip('/'))
        headers = {'Content-Type': 'application/JSON'}
        data = json.dumps(data)
        response = self.session.post(url, data=data, headers=headers)
        #logger.debug('POST %s -> %d', url, response.status_code)
        return response.json()

    def authentication(self):
        return self._get('/authentication')

    def hosts(self):
        d = self._get('/hosts')
        if 'hosts' in d:
            self._cached_hosts = d
        return getattr(self, '_cached_hosts', d)

    def _get_or_create_report(self, path, host_ids=None, fields=None):
        d = self._get(path)
        if not d or not d.get('token', None) or not d.get('expires', None):
            if host_ids is None:
                host_ids = [x['id'] for x in self.hosts().get('hosts', {})]
            elif callable(host_ids):
                host_ids = host_ids()
            if fields is None:
                fields = []
            elif callable(fields):
                fields = fields()
            post_data = {
                'hostIds': host_ids,
                'fields': fields
            }
            d = self._post(path, post_data)
        token = d.get('token', None)
        result = {'report': dict(d.items()), 'hosts': {}}
        while token:
            d = self._get('%s/%s' % (path, token))
            result['hosts'].update(d['hosts'])
            token = d['report']['token']
        return result

    def hardware_fields(self):
        return self._get('/inventory/hardware/fields')


    def hardware_report(self, host_ids=None, fields=None):
        if fields is None:
            fields = self.hardware_fields
        return self._get_or_create_report('/inventory/hardware/reports',
                                          host_ids, fields)

    def system_fields(self):
        return self._get('/inventory/system/fields')

    def system_report(self, host_ids=None, fields=None):
        if fields is None:
            fields = self.system_fields
        return self._get_or_create_report('/inventory/system/reports',
                                          host_ids, fields)
