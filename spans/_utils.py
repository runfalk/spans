"""Helper functions"""

from ._compat import *

__all__ = [
    "find_slots",
    "PicklableSlotMixin"
]

def find_slots(cls):
    """Return a set of all slots for a given class and its parents"""

    slots = set()
    for c in cls.__mro__:
        cslots = getattr(c, "__slots__", tuple())

        if not cslots:
            continue
        elif isinstance(cslots, (bstr, ustr)):
            cslots = (cslots,)

        slots.update(cslots)

    return slots

class PicklableSlotMixin(object):
    __slots__ = ()

    def __getstate__(self):
        return {attr : getattr(self, attr) for attr in find_slots(self.__class__)}

    def __setstate__(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)

def sane_total_ordering(cls):
    def __ge__(self, other):
        lt = self.__lt__(other)
        if lt is NotImplemented:
            return NotImplemented

        return not lt

    def __le__(self, other):
        lt = self.__lt__(other)
        if lt is NotImplemented:
            return NotImplemented

        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented

        return lt or eq

    def __gt__(self, other):
        le = __le__(self, other)
        if le is NotImplemented:
            return NotImplemented

        return not le

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented

        return not eq

    ops = [(f.__name__, f) for f in [__ge__, __le__, __gt__]]
    predefined = set(dir(cls))

    if "__lt__" not in predefined:
        raise ValueError("Must define __lt__")

    for func in [__ge__, __le__, __gt__, __ne__]:
        name = func.__name__

        # Test if class actually has overridden the default rich comparison
        # implementation
        if name not in predefined or getattr(cls, name) is getattr(object, name):
            setattr(cls, name, func)

    return cls
