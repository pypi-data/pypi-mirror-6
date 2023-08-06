from hashlib import sha256
try:
    from urlparse import urlparse
except ImportError:  # py3
    from urllib.parse import urlparse

import hmac
import json


from .vendor import requests


class ApiResponse(object):
    """
    This class is very basic, it simply allows
    access to the raw response as well as sets
    __nonzero__ appropriately
    """

    ok = (200, 202)

    def __init__(self, response):
        self.response = response

    def __nonzero__(self):
        return self.response.status_code in self.ok

    def __repr__(self):
        state = 'Success' if bool(self) else 'Failure'
        return '<gorealtime.client.ApiResponse (%s)>' % state


class Client(object):

    api_base = 'https://api.gorealti.me'

    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret

    @classmethod
    def from_url(cls, url):
        """
        Returns a Client object when given a URL of the format
        ``https://<app_key>:<app_secret>@api.gorealti.me``
        """
        parsed = urlparse(url)
        client = cls(parsed.username, parsed.password)
        client.api_base = '%s://%s' % (parsed.scheme, parsed.hostname)
        return client

    def push(self, message, channels):
        """
        Pushes ``message`` to all ``channels``
        """
        if isinstance(channels, basestring):
            channels = [channels]

        data = json.dumps({
            'signature': self.sign(message),
            'message': message,
            'channels': channels,
            'app': self.app_key,
        })

        r = requests.post(
            '%s/v1/push' % self.api_base,
            data=data,
            headers={'content-type': 'application/json'},
        )
        return ApiResponse(r)

    def sign(self, message):
        """
        Returns a signature made using an app's secret key
        """
        message = message.encode('ascii')
        secret = self.app_secret.encode('ascii')
        return hmac.new(secret, message, sha256).hexdigest()
