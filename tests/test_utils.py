import pytest

from datetime import date
from spans._utils import date_from_iso_week, find_slots


@pytest.mark.parametrize("args, day", [
    ((1999, 52), date(1999, 12, 27)),
    ((2000, 1), date(2000, 1, 3)),
    ((2000, 2), date(2000, 1, 10)),
    ((2009, 53), date(2009, 12, 28)),
    ((2010, 1), date(2010, 1, 4)),
])
def test_date_from_iso_week(args, day):
    assert date_from_iso_week(*args) == day


@pytest.mark.parametrize("day", [0, 8])
def test_date_from_iso_week_invalid_day_of_week(day):
    with pytest.raises(ValueError):
        date_from_iso_week(2000, 1, day_of_week=day)


def test_find_slots_single():
    class Slots(object):
        __slots__ = "single"

    assert find_slots(Slots) == {"single"}


def test_find_slots_multiple():
    class Slots(object):
        __slots__ = ("a", "b")

    assert find_slots(Slots) == {"a", "b"}
