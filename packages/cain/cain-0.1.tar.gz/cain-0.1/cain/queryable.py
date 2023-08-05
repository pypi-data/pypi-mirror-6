__author__ = 'oakfang'


class Queryable(object):
    """
    Base Queryable object
    """
    @classmethod
    def __validate__(cls):
        """
        Override to determine if code can query.
        """
        return True

    @classmethod
    def __get__(cls, *args, **kwargs):
        """
        Override to return the filtered object.
        """
        return None

    @classmethod
    def get(cls, *args, **kwargs):
        assert cls.__validate__(), "Connection can't be validated."
        return cls.__get__(*args, **kwargs)


class ElixirQueryable(Queryable):
    """
    Queryable for the elixir framework.
    """
    @classmethod
    def __validate__(cls):
        return hasattr(cls, "query")

    @classmethod
    def __get__(cls, *args, **kwargs):
        q = getattr(cls, "query")
        for arg in args:
            q = q.filter(arg)
        for key, value in kwargs.iteritems():
            q = q.filter_by(**{key: value})
        return q


__FRAMEWORKS = {'elixir': ElixirQueryable}
Queryables = {}


for framework in __FRAMEWORKS:
    try:
        module = __import__(framework)
        Queryables[module] = __FRAMEWORKS[framework]
    except ImportError:
        pass