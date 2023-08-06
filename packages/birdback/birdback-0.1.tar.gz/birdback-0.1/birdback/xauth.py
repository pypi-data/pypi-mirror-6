# -*- coding: utf-8 -*-
import hashlib
import hmac

from urllib import urlencode
from urlparse import urlparse
from requests import request
from requests.auth import AuthBase

TOKEN_ID_HEADER = 'X-Auth-Token'
TOKEN_SECRET_HEADER = 'X-Auth-Token-Secret'
SIGNATURE_HEADER = 'X-Auth-Signature'
CONSUMER_ID_HEADER = 'X-Auth-Key'


def utf8(value):
    """Returns utf-8 value for given input value.

    :param value: The value to encode.
    """
    if type(value) == unicode:
        value = value.encode('utf-8')

    return value


def compute_footprint(method, url, data):
    """Computes a footprint for given request payload.

    :param method: The Http method.
    :param url: The ressource url.
    :param datas: The request datas.
    """
    parsed = urlparse(url)
    if len(parsed.query) > 0:
        url = "%s?%s" % (parsed.path, parsed.query)
    else:
        url = parsed.path

    if data is not None and len(data) > 0:
        if hasattr(data, 'keys'):
            data = [(key, utf8(data[key])) for key in sorted(data.keys())]
            data = urlencode(data)
        else:
            data = hashlib.sha256(str(data)).hexdigest()
    else:
        data = ''

    return "%s&%s&%s" % (method.upper(), url, data)


def compute_signature(secret, method, url, data=None,
                      digestmod=hashlib.sha256):
    """Computes an hmac signature from request payload.

    :param secret: The secret key.
    :param method: The Http method.
    :param url: The ressource url.
    :param datas: The request datas.
    :param digestmod: The digest algorhythm.
    """
    footprint = compute_footprint(method, url, data)
    h = hmac.new(secret, digestmod=digestmod)
    h.update(footprint)
    return h.hexdigest()


class XAuth(AuthBase):
    SIGNATURE_HEADER = SIGNATURE_HEADER

    def __init__(self, secret, digestmod, data):
        self.secret = secret
        self.digestmod = digestmod
        self.data = data

    def __call__(self, request):
        request.headers[self.SIGNATURE_HEADER] = compute_signature(
            self.secret, request.method,
            request.url, self.data,
        )

        return request


class Client(object):
    TOKEN_ID_HEADER = TOKEN_ID_HEADER
    TOKEN_SECRET_HEADER = TOKEN_SECRET_HEADER
    CONSUMER_ID_HEADER = CONSUMER_ID_HEADER

    def __init__(self, api_url="https://api.birdback.com",
            token_url="/auth/token/", consumer_id=None,
            consumer_secret=None, token_id=None, token_secret=None,
            digestmod=hashlib.sha256, verify=True):
        """Initializes a new XAuth client.

        :param api_url: The API base url.
        :param token_url: The authentication token url.
        :param consumer_id: The consumer public_id.
        :param consumer_secret: The consumer secret.
        :param token_id: The authentication token public key.
        :param token_secret: The authentication token secret.
        :param verify: Boolean flag whether to verify SSL certificate.
        """
        self.api_url = api_url
        self.token_url = token_url
        self.consumer_id = consumer_id
        self.consumer_secret = consumer_secret
        self.token_id = token_id
        self.token_secret = token_secret
        self.digestmod = digestmod
        self.verify = verify

    def __getattr__(self, attr):
        """Act as a proxy for request.
        """
        if attr in ('get', 'post', 'put', 'patch', 'options', 'delete', ):
            return lambda url, **kwargs: self.request(attr, url, **kwargs)

    def authenticate(self, **kwargs):
        """Requests an authentication token.
        """
        r = self.get(self.token_url, **kwargs)
        self._handle_token(r.headers)
        return r

    def request(self, method, url, **kwargs):
        """Executes an Http request.

        :param method: The Http method.
        :param url: The ressource url.
        """

        headers = kwargs.pop('headers', None) or {}
        headers[self.TOKEN_ID_HEADER] = self.token_id

        url = "%s%s" % (self.api_url, url)

        #  Consumer id
        if self.consumer_id is not None:
            headers[self.CONSUMER_ID_HEADER] = self.consumer_id

        #  Signature
        if self.consumer_secret is not None or self.token_secret is not None:
            secret = self.token_secret if self.token_secret is not None else ''

            if self.consumer_secret:
                secret += self.consumer_secret

            auth = XAuth(str(secret), self.digestmod, kwargs.get('data'))

        kwargs.setdefault('verify', self.verify)

        return request(
            method, url, auth=auth, headers=headers, **kwargs
        )

    def _handle_token(self, headers):
        """Sets authentication token values from headers.

        :param request: The request headers.
        """
        if self.TOKEN_ID_HEADER in headers and \
                self.TOKEN_SECRET_HEADER in headers:
            self.token_id = headers.get(self.TOKEN_ID_HEADER)
            self.token_secret = headers.get(self.TOKEN_SECRET_HEADER)
