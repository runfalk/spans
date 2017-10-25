"""Helper functions"""

from datetime import date, datetime, timedelta

from ._compat import *

__all__ = [
    "date_from_iso_week",
    "find_slots",
    "PicklableSlotMixin",
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


class PartialOrderingMixin(object):
    __slots__ = ()

    def __le__(self, other):
        lt = self.__lt__(other)
        eq = self.__eq__(other)

        if lt is NotImplemented and eq is NotImplemented:
            return NotImplemented
        return lt is True or eq is True

    def __gt__(self, other):
        le = self.__le__(other)
        if le is NotImplemented:
            return NotImplemented
        return not le

    def __ge__(self, other):
        gt = self.__gt__(other)
        eq = self.__eq__(other)
        if gt is NotImplemented and eq is NotImplemented:
            return NotImplemented
        return gt is True or eq is True

    def __ne__(self, other):
        eq = self.__eq__(other)
        if eq is NotImplemented:
            return NotImplemented

        return not eq
