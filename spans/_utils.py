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
