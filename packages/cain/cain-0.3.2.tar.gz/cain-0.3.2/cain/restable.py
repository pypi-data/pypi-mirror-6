__author__ = 'oakfang'

import re
import json
import requests
from functools import partial


def sanitize_base(base_url):
    """
    Make sure that the url base is http or https, and doesn't end with a '/'
    """
    if not re.match('https?://', base_url):
        base_url = "http://" + base_url
    while base_url.endswith('/'):
        base_url = base_url[:-1]
    return base_url


def validate_request(r):
    """
    Validate code 200 for request
    """
    assert r.ok, "Request failed with error code {error}".format(error=r.status_code)


class FlusherSetter(object):
    """
    Automate flusher settings
    """
    def __init__(self, f, flusher, key):
        self.f = f
        self.flusher = flusher
        self.key = key

    def __call__(self, instance, value):
        flusher = getattr(instance, self.flusher)
        flusher[self.key] = self.f(instance, value)


flushersetter = lambda flusher, key: partial(FlusherSetter, flusher=flusher, key=key)


class RestfulMethod(object):
    """
    A base skeleton for REST methods
    """
    def __init__(self, f, route, base, raw=False):
        """
        :param f: function wrapped
        :param route: the route to follow
        :param base: http root
        :param raw: don't load response as json
        """
        self.f = f
        self.route = route
        self._base = None
        self.base = base
        self.raw = raw

    @property
    def base(self):
        """
        Wrapping root server url
        """
        return self._base

    @base.setter
    def base(self, value):
        """
        Sanitizing value of root url
        """
        self._base = sanitize_base(value)

    def _extract_parameters(self):
        """
        Extract instance parameters from url (marked with <>)
        """
        return re.compile('<(.*?)>').findall(self.route)

    def get_url(self, instance=None):
        """
        Resolve full url
        """
        url = self.base + self.route
        if instance:
            for prop in self._extract_parameters():
                url = url.replace('<'+prop+'>', str(getattr(instance, prop)))
        return url

    def __call__(self, *args, **kwargs):
        """
        This is the actual call
        """
        pass

    def __get__(self, instance, owner=None):
        """
        This makes it onto an instance method
        """
        return partial(self, instance)


class GETRestfulMethod(RestfulMethod):
    """
    This is a REST-ful GET method.
    It can be cached.
    """
    def __init__(self, f, route, base, raw=False, cache=None):
        """
        :param f: function wrapped
        :param route: the route to follow
        :param base: http root
        :param raw: don't load response as json
        :param cache: cache for this route
        """
        super(GETRestfulMethod, self).__init__(f, route, base, raw)
        self.cache = cache

    def _get_from_cache(self, url, instance):
        if self.cache and url in self.cache:
            value = self.cache[url]
            return self.f(instance, json.loads(value) if not self.raw else value)
        return None

    def _get_request_value(self, url, params=None):
        r = requests.get(url, params=params if params else {})
        validate_request(r)
        return r.text

    def __call__(self, instance):
        url = self.get_url(instance)
        cache_value = self._get_from_cache(url, instance)
        if cache_value:
            return cache_value
        value = self._get_request_value(url)
        if self.f.func_code.co_argcount == 1:
            return self.f(instance)
        if self.cache:
            self.cache[url] = value
        return self.f(instance, json.loads(value) if not self.raw else value)


class GETRestfulProperty(GETRestfulMethod):
    """
    This is a REST-ful GET property.
    It can be cached.
    It can be set with a putter callback.
    """
    def __get__(self, instance, owner=None):
        return self(instance)

    def putter(self, callback):
        self._setter = callback

    def __set__(self, instance, value):
        if not hasattr(self, '_setter'):
            raise AttributeError('This attribute cannot be set')
        self._setter(instance, value)


class GETRestfulQueryStaticMethod(GETRestfulMethod):
    """
    This is a REST-ful GET query that tries to returns elements of owner.
    """
    def __get__(self, instance, owner=None):
        return partial(self, owner)

    def __call__(self, owner, *args, **kwargs):
        params = self.f(*args, **kwargs)
        url = self.get_url()
        value = self._get_request_value(url, params)
        if self.raw:
            return value
        if hasattr(owner, '__rest__'):
            return (owner.__rest__(val) for val in json.loads(value))
        return json.loads(value)


class DELETERestfulMethod(RestfulMethod):
    """
    This is a REST-ful DELETE method.
    """
    def __call__(self, instance):
        r = requests.delete(self.get_url(instance))
        validate_request(r)
        return self.f(instance)


class PUTRestfulMethod(RestfulMethod):
    """
    This is a REST-ful PUT method.
    """
    def __call__(self, instance, *args, **kwargs):
        edited = self.f(instance, *args, **kwargs)
        r = requests.put(self.get_url(instance), edited)
        validate_request(r)
        return json.loads(r.text) if not self.raw else r.text


class POSTRestfulFunction(RestfulMethod):
    """
    This is a REST-ful POST static function.
    """
    def __call__(self, owner, *args, **kwargs):
        edited = self.f(*args, **kwargs)
        r = requests.post(self.get_url(), edited)
        validate_request(r)
        if self.raw:
            return r.text
        if hasattr(owner, '__rest__'):
            return owner.__rest__(json.loads(r.text))
        return json.loads(r.text)

    def __get__(self, instance, owner=None):
        return partial(self, owner)


class RestfulApplication(object):
    """
    Base Restful Application instance for use in module.
    """
    def __init__(self, base_url):
        self.base = sanitize_base(base_url)
        self._cache = {}

    def purge(self):
        self._cache.clear()

    def get(self, route, raw=False, cache=True):
        def _outer(f):
            return GETRestfulProperty(f, route, self.base, raw, self._cache if cache else None)
        return _outer

    def route(self, route, raw=False, cache=True):
        def _outer(f):
            return GETRestfulMethod(f, route, self.base, raw, self._cache if cache else None)
        return _outer

    def query(self, route, raw=False):
        def _outer(f):
            return GETRestfulQueryStaticMethod(f, route, self.base, raw, None)
        return _outer

    def post(self, route, raw=False):
        def _outer(f):
            return POSTRestfulFunction(f, route, self.base, raw)
        return _outer

    def put(self, route, raw=False):
        def _outer(f):
            return PUTRestfulMethod(f, route, self.base, raw)
        return _outer

    def delete(self, route, raw=False):
        def _outer(f):
            return DELETERestfulMethod(f, route, self.base, raw)
        return _outer

    def flusher(self, restful_instance, route):
        return PutFlusher(self, restful_instance, route)


class PutFlusher(dict):
    """
    This is a dict you can flush onto a url, connected to a restful instance.
    """
    def __init__(self, restful_app, restful_instance, route, *args, **kwargs):
        super(PutFlusher, self).__init__(*args, **kwargs)
        self.flush = partial(PUTRestfulMethod(lambda x: self._flush(), route, restful_app.base), restful_instance)

    def _flush(self):
        r = self.copy()
        self.clear()
        return r