import requests

from requests_auth_mashery import MasheryAuth


class MasheryReportingApi(object):
    """
    This API enables customers to retrieve performance and operational data, for
    their Mashery-managed APIs, in order to drive off-line analytics, custom
    dashboards and integrate into their own datawarehouses. This API, which can
    be used with your existing Mashery V2 API key, exposes most of the data that
    can already be seen in the Mashery Dashboard.

    http://support.mashery.com/docs/read/mashery_api/20_reporting
    """

    BASE_URL = 'http://api.mashery.com/v2/rest'

    def __init__(self, site_id, service_key, api_key, api_secret):
        self.site_id = site_id
        self.service_key = service_key

        self.base_url = '%s/%s/reports/calls' % (self.BASE_URL, self.site_id)

        session = requests.Session()
        session.auth = MasheryAuth(api_key, api_secret)
        self.session = session

    def make_request(self, path, params=None):
        """
        Makes the API request to Mashery. Used by the other methods in
        this class.
        """

        if params is None:
            params = {}

        params['format'] = 'json'

        url = self.base_url + path

        r = self.session.get(url=url, params=params)

        r.raise_for_status()

        payload = r.json()

        if 'errorcode' in payload:
            raise Exception(payload['errorcode'])

        return payload

    def developer_activity_for_service(self, start_date, end_date, limit=10):
        """
        For a specific service, returns a summary across the report interval of
        activity by Developer. Sort order of the returned data is number of
        successful calls for each developer, in descending order.
        """

        path = '/developer_activity/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'limit': limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def errorcodes_for_service(self, start_date, end_date, errorcode_limit=10):
        """
        For a specific service, returns time-based counts of errors
        """

        path = '/errorcodes/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'errorcode_limit': errorcode_limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def errorcodes_for_service_for_developer(self, service_dev_key, start_date,
                                             end_date, errorcode_limit=10):
        """
        For a specific service, for a specific developer, call count by
        error code.
        """

        path = '/errorcodes/service/%(service_key)s/developer/%(service_dev_key)s' % {
            'service_key': self.service_key,
            'service_dev_key': service_dev_key
        }

        params = {
            'errorcode_limit': errorcode_limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def errorcount_by_developer_for_service(self, start_date, end_date,
                                            limit=10):
        """
        For a specific service, returns error count broken out by Developer
        """

        path = '/errorcount_by_developer/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'limit': limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def errorcount_by_method_for_service(self, start_date, end_date, limit=10):
        """
        For a specific service, returns time-based counts of errors further
        broken out by Method
        """

        path = '/errorcount_by_method/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'limit': limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def geolocation_for_service(self, start_date, end_date):
        """
        For a specific service, returns a summary across the report interval of
        originating geolocation of calls
        """

        path = '/geolocation/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def geolocation_for_service_for_developer(self, service_dev_key, start_date,
                                              end_date, limit=10):
        """
        For a specific service and developer, returns a summary across the
        report interval of originating geolocation of calls
        """

        path = '/geolocation/service/%(service_key)s/developer/%(service_dev_key)s' % {
            'service_key': self.service_key,
            'service_dev_key': service_dev_key
        }

        params = {
            'limit': limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def latency_for_service(self, start_date, end_date):
        """
        For a specific service, returns time-based average of call latency
        breaking out Mashery Proxy and the Client API
        """

        path = '/latency/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def latency_by_method_for_service(self, start_date, end_date,
                                      method_limit=10):
        """
        For a specific service, returns time-based average of call latency
        further broken out by Method
        """

        path = '/latency_by_method/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'method_limit': method_limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def latency_by_responsecode_for_service(self, start_date, end_date):
        """
        For a specific service, returns time-based average of call latency
        further broken out by response code
        """

        path = '/latency_by_responsecode/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def median_volume_by_hour_for_service(self, start_date, end_date):
        """
        For a specific service, across the specified interval, returns median
        call volume by hour for a 24-hour day.
        """

        path = '/median_volume_by_hour/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def methods_for_service(self, start_date, end_date, method_limit=10):
        """
        For a specific service, returns time-based count of calls by method
        """

        path = '/methods/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'method_limit': method_limit,
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def methods_for_service_for_developer(self, service_dev_key, start_date,
                                          end_date):
        """
        For a specific service, for a specific developer, call count by method.
        """

        path = '/methods/service/%(service_key)s/developer/%(service_dev_key)s' % {
            'service_key': self.service_key,
            'service_dev_key': service_dev_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def responses_from_cache_for_service(self, start_date, end_date):
        """
        For a specific service, returns time-based percentage of successful call
        responses that were from Mashery Cache
        """

        path = '/responses_from_cache/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def status_for_service(self, start_date, end_date):
        """
        For a specific service, returns time-based count of calls by status
        """

        path = '/status/service/%(service_key)s' % {
            'service_key': self.service_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)

    def status_for_service_for_developer(self, service_dev_key, start_date,
                                         end_date):
        """
        Call status for a specific service and a specific developer.
        """

        path = '/status/service/%(service_key)s/developer/%(service_dev_key)s' % {
            'service_key': self.service_key,
            'service_dev_key': service_dev_key
        }

        params = {
            'start_date': start_date,
            'end_date': end_date,
        }

        return self.make_request(path, params)
