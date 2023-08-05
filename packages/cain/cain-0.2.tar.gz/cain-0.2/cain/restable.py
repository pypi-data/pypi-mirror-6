__author__ = 'oakfang'

import re
import json
import requests
from functools import partial


def sanitize_base(base_url):
    if not re.match('https?://', base_url):
        base_url = "http://" + base_url
    while base_url.endswith('/'):
        base_url = base_url[:-1]
    return base_url


def validate_request(r):
    assert r.ok, "Request failed with error code {error}".format(error=r.status_code)


class RestfulMethod(object):
    def __init__(self, f, route, base=None, raw=False):
        self.f = f
        self.route = route
        self._base = None
        if base:
            self.base = base
        self.raw = raw

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        self._base = sanitize_base(value)

    def _extract_parameters(self):
        return re.compile('<(.*?)>').findall(self.route)

    def get_url(self, instance=None):
        url = self.base + self.route
        if instance:
            for prop in self._extract_parameters():
                url = url.replace('<'+prop+'>', str(getattr(instance, prop)))
        return url

    def __call__(self, *args, **kwargs):
        pass

    def __get__(self, instance, owner=None):
        return partial(self, instance)


class GETRestfulMethod(RestfulMethod):
    def __call__(self, instance):
        r = requests.get(self.get_url(instance))
        validate_request(r)
        return self.f(instance,
                      json.loads(r.text) if not self.raw else r.text) \
            if self.f.func_code.co_argcount == 2 else self.f(instance)


class GETRestfulProperty(GETRestfulMethod):
    def __get__(self, instance, owner=None):
        return self(instance)


class DELETERestfulMethod(RestfulMethod):
    def __call__(self, instance):
        r = requests.delete(self.get_url(instance))
        validate_request(r)
        return self.f(instance)


class PUTRestfulMethod(RestfulMethod):
    def __call__(self, instance, *args, **kwargs):
        edited = self.f(instance, *args, **kwargs)
        r = requests.put(self.get_url(instance), edited)
        validate_request(r)
        return json.loads(r.text) if not self.raw else r.text


class POSTRestfulFunction(RestfulMethod):
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
    def __init__(self, base_url):
        self.base = base_url

    def get(self, route, raw=False):
        def _outer(f):
            return GETRestfulProperty(f, route, self.base, raw)
        return _outer

    def route(self, route, raw=False):
        def _outer(f):
            return GETRestfulMethod(f, route, self.base, raw)
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