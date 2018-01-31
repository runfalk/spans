"""Compatibility module for python 3"""

import re
import sys

__all__ = [
    "add_metaclass",
    "fix_timedelta_repr",
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


def fix_timedelta_repr(func):
    """
    Account repr change for timedelta in Python 3.7 and above in docstrings.

    This is needed to make some doctests pass on Python 3.7 and above. This
    change was introduced by `bpo-30302 <https://bugs.python.org/issue30302>`_
    """
    # We don't need to do anything if we're not on 3.7 or above
    if version < (3, 7):
        return func

    def fix_timedelta(match):
        values = match.group(1).split(", ")
        param_repr = ", ".join(
            "{}={}".format(param, value)
            for param, value in zip(("days", "seconds", "microseconds"), values)
            if value != "0"
        )

        # If we have a zero length timedelta it should be represented as
        # timedelta(0), i.e. without named parameters
        if not param_repr:
            param_repr = "0"

        return "timedelta({})".format(param_repr)

    func.__doc__ = re.sub(r"timedelta\(([^)]+)\)", fix_timedelta, func.__doc__)
    return func
