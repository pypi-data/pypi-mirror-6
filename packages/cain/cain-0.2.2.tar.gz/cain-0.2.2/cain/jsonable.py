__author__ = 'oakfang'

import json

iterable = (list, tuple, dict)


class JsonableEncoder(json.JSONEncoder):
    """
    A default encoder for Jsonable objects.
    """
    def default(self, o):
        return o.__jencode__()


class Jsonable(object):
    """
    Jsonable Mixin
    ==============
    Use the static property __jattrs__ to indicate the attributes you'd like to export.
    """
    __jattrs__ = []

    def __jencode__(self):
        """
        Override this to implement a smarter way of self encoding.
        """
        jdict = {attr: raw_json(getattr(self, attr)) for attr in self.__jattrs__}
        return jdict

    @classmethod
    def __jdecode__(cls, string):
        """
        Override this to implement a better decoder.
        :param string: json string to decode.
        """
        attr_dict = json.loads(string)
        return cls(**attr_dict)


def raw_json(obj):
    """
    Recursively create a dump-able object to jsonify.
    """
    if isinstance(obj, Jsonable):
        return JsonableEncoder().default(obj)
    if isinstance(obj, iterable):
        if isinstance(obj, dict):
            return {raw_json(key): raw_json(value) for key, value in obj.iteritems()}
        else:
            return map(raw_json, obj)
    return obj


def jsonify(obj):
    """
    Turn an object to a JSON-encoded string.
    """
    return json.dumps(raw_json(obj))


def objectify(jstring, as_type=None):
    """
    Try to decode JSON-encoded string as a certain Jsonable object, or just load it regularly.
    """
    if as_type is None:
        return json.loads(jstring)
    if not issubclass(as_type, Jsonable):
        raise TypeError("Pass Jsonable objects only")
    return json.JSONDecoder(object_hook = as_type.__jdecode__).decode(jstring)