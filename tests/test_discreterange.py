import pytest

from datetime import date, timedelta
from spans import intrange, daterange


def test_last():
    assert intrange(1).last is None


@pytest.mark.parametrize("a, b", [
    (intrange(1, 10), range(1, 10)),
    (
        daterange(date(2000, 1, 1), date(2000, 1, 10)),
        (date(2000, 1, i) for i in range(1, 10))
    ),
])
def test_iteration(a, b):
    assert list(a) == list(b)
