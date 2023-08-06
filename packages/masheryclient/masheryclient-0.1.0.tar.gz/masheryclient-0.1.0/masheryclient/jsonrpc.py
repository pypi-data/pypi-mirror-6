import json

import requests

from requests_auth_mashery import MasheryAuth


class MasheryObjectType(object):
    """
    A Member object stores contact information for API key owners and allows
    developer portal access.
    """
    MEMBER = 'member'

    """
    An Application is the name of the client system that a developer is building
    that consumes either Packages or Services.
    """
    APPLICATION = 'application'

    """
    A Key tracks access to your Service.
    """
    KEY = 'key'

    """
    A Package Key tracks access to your Package.
    """
    PACKAGE_KEY = 'package_key'

    """
    A group of Plans.
    """
    PACKAGE = 'package'

    """
    A specific set of rules that define access to Services.
    """
    PLAN = 'plan'

    """
    A Service object describes a proxy service.  It also contains one or
    more Endpoints.
    """
    SERVICE = 'service'

    """
    A Role groups members and controls access to portal features and content.
    """
    ROLE = 'role'

    """
    """
    DEVELOPER_CLASS = 'developer_class'


class MasheryJsonRpcApi(object):
    """
    Make JSON-RPC 2.0 request to the Mashery 2.0 API

    http://support.mashery.com/docs/read/mashery_api/20
    """

    MASHERY_API_BASE = 'http://api.mashery.com/v2/json-rpc'

    def __init__(self, site_id, service_key, api_key, api_secret):
        self.site_id = site_id
        self.service_key = service_key

        session = requests.Session()
        session.auth = MasheryAuth(api_key, api_secret)
        self.session = session

    def make_request(self, method, params=None):
        """
        Makes the JSON-RPC 2.0 API call and returns the unwrapped result.
        """
        if params is None:
            params = []

        payload = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain',
        }

        url = '%s/%s' % (self.MASHERY_API_BASE, self.site_id)

        r = self.session.post(url=url, headers=headers, data=json.dumps(payload))
        r.raise_for_status()

        payload = r.json()['result']

        return payload

    def fetch(self, object_type, identifier):
        """
        Fetch an object by it's primary identifier. See the table below for
        which field ob the object to use.

        =========== ================== =========
        Object Type Primary Identifier JSON Type
        =========== ================== =========
        application id                 integer
        member      username           string
        key         id                 integer
        role        id                 integer
        service     service_key        string
        =========== ================== =========
        """
        method = '%s.fetch' % object_type
        params = [identifier]

        return self.make_request(method, params)

    def fetch_key_by_api_key(self, api_key):
        """
        Shortcut method for retrieving a Key object by `apikey` instead of by
        ID. It's more common that you'll just have the value of `apikey` field.
        """
        identifier = [{
            'service_key': self.service_key,
            'apikey': api_key,
        }]

        return self.fetch('key', identifier)

    def query(self, query):
        """
        Ad-hoc queries for objects.

        http://support.mashery.com/docs/read/mashery_api/20/Query_Language
        """
        return self.make_request('object.query', [query])
