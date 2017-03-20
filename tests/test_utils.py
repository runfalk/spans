import pytest

from datetime import date
from spans._utils import date_from_iso_week


@pytest.mark.parametrize("args, day", [
    ((1999, 52), date(1999, 12, 27)),
    ((2000, 1), date(2000, 1, 3)),
    ((2000, 2), date(2000, 1, 10)),
])
def test_date_from_iso_week(args, day):
    assert date_from_iso_week(*args) == day
