from base64 import b64encode
import logging
import os
import xml.etree.ElementTree as ET

from requests.exceptions import HTTPError
import requests

from . import exceptions
from .models import AccessToken
from .throttle import Throttler
from .throttle.storages import SQLite

log = logging.getLogger(__name__)


def make_service_request_url(
    client, service, reference_type, input, endpoint, constituents
):
    parts = [
        client.__service_url_prefix__, service, reference_type,
        input and input.__class__.__name__.lower(), endpoint,
        ','.join(constituents)
    ]
    return os.path.join(*filter(None, parts))


class Client(object):
    __auth_url__ = 'https://ops.epo.org/3.1/auth/accesstoken'
    __service_url_prefix__ = 'https://ops.epo.org/3.1/rest-services'
    __family_path__ = 'family'
    __published_data_path__ = 'published-data'
    __published_data_search_path__ = 'published-data/search'

    def __init__(self, accept_type='xml', throttle_history_storage=None):
        self.accept_type = 'application/{}'.format(accept_type)
        self.throttler = Throttler(throttle_history_storage or SQLite())

    def check_for_exceeded_quota(self, response):
        if (response.status_code != 403) or \
           ('X-Rejection-Reason' not in response.headers):
            return response

        reasons = (
            'AnonymousQuotaPerMinute',
            'AnonymousQuotaPerDay',
            'IndividualQuotaPerHour',
            'RegisteredQuotaPerWeek',
        )

        rejection = response.headers['X-Rejection-Reason']

        for reason in reasons:
            if reason.lower() in rejection.lower():
                try:
                    response.raise_for_status()
                except HTTPError as e:
                    klass = getattr(exceptions, '{}Exceeded'.format(reason))
                    e.__class__ = klass
                    raise
        return response  # pragma: no cover

    def post(self, url, data, extra_headers=None):
        headers = {'Accept': self.accept_type}
        headers.update(extra_headers or {})
        return self.throttler.post(url, data=data, headers=headers)

    def make_request(self, url, data, extra_headers=None):
        response = self.post(url, data, extra_headers)
        response = self.check_for_exceeded_quota(response)
        response.raise_for_status()
        return response

    # Service requests
    def _service_request(
        self, path, reference_type, input, endpoint, constituents
    ):
        url = make_service_request_url(
            self, path, reference_type, input, endpoint, constituents or []
        )
        return self.make_request(url, input.as_api_input())

    def published_data(
        self, reference_type, input, endpoint='biblio', constituents=None
    ):
        return self._service_request(
            self.__published_data_path__, reference_type, input, endpoint,
            constituents
        )

    def family(self, reference_type, input, endpoint=None, constituents=None):
        return self._service_request(
            self.__family_path__, reference_type, input, endpoint, constituents
        )

    def published_data_search(
        self, cql, range_begin=1, range_end=25, constituents=None
    ):
        url = make_service_request_url(
            self, self.__published_data_search_path__, None, None, None,
            constituents or []
        )
        return self.make_request(
            url,
            {'q': cql},
            {'X-OPS-Range': '{}-{}'.format(range_begin, range_end)}
        )


class RegisteredClient(Client):
    def __init__(
        self, key, secret, accept_type='xml', throttle_history_storage=None
    ):
        super(RegisteredClient, self).__init__(
            accept_type, throttle_history_storage or SQLite()
        )
        self.key = key
        self.secret = secret
        self._access_token = None

    def acquire_token(self):
        headers = {
            'Authorization': 'Basic {}'.format(
                b64encode('{}:{}'.format(self.key, self.secret))
            ),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = {'grant_type': 'client_credentials'}
        response = requests.post(
            self.__auth_url__, headers=headers, data=payload
        )
        response.raise_for_status()
        self._access_token = AccessToken(response)

    @property
    def access_token(self):
        #TODO: Custom auth handler plugin to requests?
        if (not self._access_token) or \
           (self._access_token and self._access_token.is_expired):
            self.acquire_token()
        return self._access_token

    def check_for_expired_token(self, response):
        if response.status_code != 400:
            return response

        message = ET.fromstring(response.content)
        if message.findtext('description') == 'Access token has expired':
            self.acquire_token()
            response = self.make_request(
                response.request.url, response.request.body
            )
        return response

    def make_request(self, url, data, extra_headers=None):
        extra_headers = extra_headers or {}
        token = 'Bearer {}'.format(self.access_token.token)
        extra_headers['Authorization'] = token

        response = self.post(url, data, extra_headers)
        response = self.check_for_expired_token(response)
        response = self.check_for_exceeded_quota(response)
        response.raise_for_status()
        return response
