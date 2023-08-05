# Copyright 2013 Canonical Ltd. This software is licensed under
# the GNU Affero General Public License version 3 (see the file
# LICENSE).

from __future__ import unicode_literals

try:
    str = unicode
except NameError:
    pass  # Forward compatibility with Py3k

import logging

from datetime import datetime

from requests_oauthlib import OAuth1

from ssoclient.v2.http import ApiSession
from ssoclient.v2 import errors


logger = logging.getLogger(__name__)


def datetime_from_string(value):
    """Parse a string value representing a date in isoformat."""
    try:
        result = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        result = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    return result


def parse_datetimes(value):
    """Recursively look for dates and try to parse them into datetimes."""
    assert isinstance(value, dict)
    result = value.copy()
    for k, v in value.items():
        if isinstance(v, dict):
            result[k] = parse_datetimes(v)
        elif isinstance(v, list):
            result[k] = [parse_datetimes(i) for i in v]
        elif 'date' in k:
            result[k] = datetime_from_string(v)
    return result


class V2ApiClient(object):
    """High-level client for theV2.0 API SSO resources."""

    def __init__(self, endpoint):
        self.session = ApiSession(endpoint)

    def _unicode_credentials(self, credentials):
        # if openid and credentials come directly from a call to client.login
        # then whether they are unicode or byte-strings depends on which
        # json library is in use.
        # oauthlib requires them to be unicode - so we coerce to be sure.
        if credentials is not None:
            consumer_key = str(credentials.get('consumer_key', ''))
            consumer_secret = str(credentials.get('consumer_secret', ''))
            token_key = str(credentials.get('token_key', ''))
            token_secret = str(credentials.get('token_secret', ''))
            oauth = OAuth1(
                consumer_key,
                consumer_secret,
                token_key, token_secret,
            )
        else:
            oauth = None
        return oauth

    def _merge(self, data, extra):
        """Allow data to passed to functions by keyword or by dict."""
        if data:
            data.update(extra)
        else:
            data = extra
        return data

    def register(self, data=None, **kwargs):
        response = self.session.post(
            '/accounts', data=self._merge(data, kwargs))
        result = parse_datetimes(response.content)
        return result

    def login(self, data=None, **kwargs):
        response = self.session.post(
            '/tokens/oauth', data=self._merge(data, kwargs))
        result = parse_datetimes(response.content)
        return result

    def account_details(self, openid, token=None, expand=False):
        openid = str(openid)
        oauth = self._unicode_credentials(token)
        url = '/accounts/%s?expand=%s' % (openid, str(expand).lower())

        response = self.session.get(url, auth=oauth)
        result = parse_datetimes(response.content)
        return result

    def email_delete(self, email, credentials):
        oauth = self._unicode_credentials(credentials)
        response = self.session.delete('/emails/%s' % email, auth=oauth)
        return response.status_code == 204

    def email_details(self, email, credentials):
        oauth = self._unicode_credentials(credentials)

        response = self.session.get('/emails/%s' % email, auth=oauth)
        result = parse_datetimes(response.content)
        return result

    def token_delete(self, token_key, credentials):
        oauth = self._unicode_credentials(credentials)
        response = self.session.delete(
            '/tokens/oauth/%s' % token_key, auth=oauth)
        return response.status_code == 204

    def token_details(self, token_key, credentials):
        oauth = self._unicode_credentials(credentials)

        response = self.session.get('/tokens/oauth/%s' % token_key, auth=oauth)
        result = parse_datetimes(response.content)
        return result

    def validate_request(self, data=None, **kwargs):
        """Validate an OAuth signature.

        The OAuth signature can be given either as the value of the
        Authorization header, or as a query string with the OAuth information
        in it. Expected parameters are:

        * 'http_url'
        * 'http_method'
        * 'authorization' and/or 'query_string' (at least one)

        Return a dictionary with a 'is_valid' field that indicates whether the
        given OAuth signature is valid or not.

        """
        data = self._merge(data, kwargs)
        authorization = data.get('authorization')
        query_string = data.get('query_string')

        if not authorization and not query_string:
            msg = ('Got an empty QUERY_STRING and no HTTP_AUTHORIZATION '
                   'set, at least one should be defined')
            logger.error(
                'validate_request: %s, raising ClientError.', msg)
            raise errors.ClientError(msg=msg)

        http_url = data.get('http_url', '')
        if not isinstance(http_url, str):
            try:
                data['http_url'] = http_url.decode('utf-8')
            except UnicodeError:
                msg = ('Given http_url %r can not be utf-8 decoded' % http_url)
                logger.error(
                    'validate_request: %s, raising ClientError.', msg)
                raise errors.ClientError(msg=msg)

        response = self.session.post('/requests/validate', data=data)
        return response.content

    def request_password_reset(self, email, token=None):
        response = self.session.post(
            '/tokens/password', data=dict(email=email, token=token))
        return response.content
