
import requests


class MethodMismatch(Exception):
    pass


class API(object):
    def __init__(self, server='manage.jujucharms.com', version=3, secure=True,
                 port=None, proxy_info=None):
        self.server = server
        self.protocol = 'https' if secure else 'http'
        self.port = port
        self.version = version
        self.proxy = proxy_info

    def get(self, endpoint, params={}):
        return self._fetch_json(endpoint, params, 'get')

    def post(self, endpoint, params={}):
        return self._fetch_json(endpoint, params, 'post')

    def _fetch_json(self, endpoint, params={}, method='get'):
        r = self._fetch_request(endpoint, params, method)
        return r.json()

    def _fetch_request(self, endpoint, params={}, method='get'):
        if not method.lower() in ['get', 'post']:
            raise MethodMismatch('%s is not get or post' % method)

        if method == 'post':
            r = requests.post(self._build_url(endpoint), data=params)
        elif method == 'get':
            r = requests.get(self._build_url(endpoint), params=params)

        return r

    def _earl(self):
        if self.port:
            return '%s://%s:%s' % (self.protocol, self.server, self.port)

        return '%s://%s' % (self.protocol, self.server)

    def _build_url(self, endpoint):
        url = self._earl()
        if not endpoint[0] == '/':
            endpoint = '/%s' % endpoint

        return '%s/api/%s%s' % (self._earl(), self.version, endpoint)
