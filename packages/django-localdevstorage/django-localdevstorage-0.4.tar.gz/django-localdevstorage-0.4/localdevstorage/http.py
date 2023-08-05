from cStringIO import StringIO
import urlparse
import warnings
import requests

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from localdevstorage.base import BaseStorage


class HttpStorage(BaseStorage):
    def __init__(self, location=None, base_url=None, fallback_url=None, fallback_domain=None):
        self.fallback_url = fallback_url or getattr(settings, 'LOCALDEVSTORAGE_HTTP_FALLBACK_URL', None)
        if self.fallback_url:
            warnings.warn('fallback_url and LOCALDEVSTORAGE_HTTP_FALLBACK_URL have been replaced by fallback_domain and LOCALDEVSTORAGE_HTTP_FALLBACK_DOMAIN, respectively, and will be removed in a future release.')
        self.fallback_domain = fallback_domain or getattr(settings, 'LOCALDEVSTORAGE_HTTP_FALLBACK_DOMAIN', None)
        if not (self.fallback_url or self.fallback_domain):
            raise ImproperlyConfigured('please define LOCALDEVSTORAGE_HTTP_FALLBACK_DOMAIN in your settings')
        self.session = requests.Session()
        username = getattr(settings, 'LOCALDEVSTORAGE_HTTP_PASSWORD', None)
        password = getattr(settings, 'LOCALDEVSTORAGE_HTTP_USERNAME', None)
        if username and password:
            self.session.auth = (username, password)
        super(BaseStorage, self).__init__(location, base_url)

    def _exists(self, name):
        try:
            response = self.session.head(self._path(name))
            return response.status_code == 200
        except Exception:
            return False

    def _path(self, name):
        if self.fallback_domain:
            return urlparse.urljoin(self.fallback_domain, self.url(name))
        return self.fallback_url + name

    def _get(self, name):
        response = self.session.get(self._path(name))
        if response.status_code != 200:
            raise IOError()
        return StringIO(response.content)
