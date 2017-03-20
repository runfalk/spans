"""Helper functions"""

from datetime import date, datetime, timedelta

from ._compat import *

__all__ = [
    "date_from_iso_week",
    "find_slots",
    "PicklableSlotMixin",
    "sane_total_ordering",
]

def date_from_iso_week(year, week, day_of_week=None):
    if day_of_week is None:
        day_of_week = 1

    if not 1 <= day_of_week <= 7:
        raise ValueError(
            "Day of week is not in range 1 through 7, got {!r}".format(day_of_week))

    day = datetime.strptime(
        "{:04d}-{:02d}-{:d}".format(year, week, day_of_week), "%Y-%W-%w")

    # ISO week 1 is defined as the first week to have 4 or more days in January.
    # Python's built-in date parsing considers the week that contain the first
    # Monday of the year to be the first week.
    if date(year, 1, 4).isoweekday() > 4:
        day -= timedelta(days=7)

    return day.date()


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
