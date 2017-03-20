"""Compatibility module for python 3"""

import sys

__all__ = [
    "add_metaclass",
    "is_python2",
    "iter_range",
    "bstr",
    "uchr",
    "ustr",
    "version",
]

version = sys.version_info[:2]

if version >= (3, 0):
    is_python2 = False

    if version < (3, 3):
        raise ImportError("Module is only compatible with Python (<=2.7, >=3.3)")

    bstr = bytes
    ustr = str
    uchr = chr
    iter_range = range
else:
    is_python2 = True

    bstr = str
    ustr = unicode
    uchr = unichr
    iter_range = xrange


def add_metaclass(metaclass):
    """
    Class decorator for creating a class with a metaclass. Shamelessly copied from
    Six (https://bitbucket.org/gutworth/six).

    .. code-block:: python

        @add_metaclass(MetaClass)
        def NormalClass(object):
            pass

    """

    def wrapper(cls):
        orig_vars = cls.__dict__.copy()
        slots = orig_vars.get('__slots__')

        if slots is not None:
            if isinstance(slots, str):
                slots = [slots]

            for slots_var in slots:
                orig_vars.pop(slots_var)

        orig_vars.pop('__dict__', None)
        orig_vars.pop('__weakref__', None)

        return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper
