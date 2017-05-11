import pytest

from datetime import date, datetime, timedelta
from spans import daterange


def test_datetime_type_check():
    with pytest.raises(TypeError):
        daterange(datetime(2000, 1, 1))

    with pytest.raises(TypeError):
        daterange(upper=datetime(2000, 1, 1))


def test_offset():
    range_low = daterange(date(2000, 1, 1), date(2000, 1, 6))
    range_high = daterange(date(2000, 1, 5), date(2000, 1, 10))

    assert range_low != range_high
    assert range_low.offset(timedelta(days=4)) == range_high
    assert range_low == range_high.offset(timedelta(days=-4))


def test_from_date():
    date_start = date(2000, 1, 1)
    assert daterange.from_date(date_start) == \
        daterange(date_start, date_start + timedelta(1))


@pytest.mark.parametrize("day, span", [
    (date(2000, 1, 1), daterange(date(1999, 12, 27), date(2000, 1, 3))),
    (date(2000, 1, 2), daterange(date(1999, 12, 27), date(2000, 1, 3))),
    (date(2000, 1, 3), daterange(date(2000, 1, 3), date(2000, 1, 10))),
])
def test_from_date_week(day, span):
    assert daterange.from_date(day, period="week") == span


@pytest.mark.parametrize("day, span", [
    (date(2000, 1, 1), daterange(date(1999, 12, 26), date(2000, 1, 2))),
    (date(2000, 1, 2), daterange(date(2000, 1, 2), date(2000, 1, 9))),
    (date(2000, 1, 3), daterange(date(2000, 1, 2), date(2000, 1, 9))),
])
def test_from_date_american_week(day, span):
    assert daterange.from_date(day, period="american_week") == span


@pytest.mark.parametrize("day, span", [
    (date(2000, 1, 1), daterange(date(2000, 1, 1), date(2000, 1, 31), upper_inc=True)),
    (date(2000, 2, 15), daterange(date(2000, 2, 1), date(2000, 2, 29), upper_inc=True)),
    (date(2001, 2, 15), daterange(date(2001, 2, 1), date(2001, 2, 28), upper_inc=True)),
])
def test_from_date_month(day, span):
    assert daterange.from_date(day, period="month") == span


@pytest.mark.parametrize("day, span", [
    (date(2000, 1, 1), daterange(date(2000, 1, 1), date(2000, 3, 31), upper_inc=True)),
    (date(2000, 2, 15), daterange(date(2000, 1, 1), date(2000, 3, 31), upper_inc=True)),
    (date(2000, 3, 31), daterange(date(2000, 1, 1), date(2000, 3, 31), upper_inc=True)),
])
def test_from_date_quarter(day, span):
    assert daterange.from_date(day, period="quarter") == span


@pytest.mark.parametrize("day, span", [
    (date(2000, 1, 1), daterange(date(2000, 1, 1), date(2001, 1, 1))),
    (date(2000, 6, 1), daterange(date(2000, 1, 1), date(2001, 1, 1))),
    (date(2000, 12, 31), daterange(date(2000, 1, 1), date(2001, 1, 1))),
])
def test_from_date_year(day, span):
    assert daterange.from_date(day, period="year") == span


@pytest.mark.parametrize("param", [
    True,
    1,
    1.0,
    datetime(2000, 1, 1),
])
def test_from_date_type_check(param):
    with pytest.raises(TypeError):
        daterange.from_date(param)


@pytest.mark.parametrize("period", [
    "Year",
    "YEAR",
    "foobar",
])
def test_from_date_period_check(period):
    with pytest.raises(ValueError):
        daterange.from_date(date(2000, 1, 1), period=period)


@pytest.mark.parametrize("year, iso_week, first_day", [
    (2000, 1, date(2000, 1, 3)),
    (2000, 2, date(2000, 1, 10)),
    (2000, 3, date(2000, 1, 17)),
    (2000, 4, date(2000, 1, 24)),
])
def test_from_week(year, iso_week, first_day):
    assert daterange.from_week(year, iso_week) == daterange.from_date(
        first_day, period="week")


@pytest.mark.parametrize("year", [
    2000,
    2001,
])
@pytest.mark.parametrize("month", range(1, 13))
def test_from_month(year, month):
    assert daterange.from_month(year, month) == daterange.from_date(
        date(year, month, 1), period="month")


@pytest.mark.parametrize("year, quarter, first_day", [
    (2000, 1, date(2000, 1, 1)),
    (2000, 2, date(2000, 4, 1)),
    (2000, 3, date(2000, 7, 1)),
    (2000, 4, date(2000, 10, 1)),
])
def test_from_quarter(year, quarter, first_day):
    assert daterange.from_quarter(year, quarter) == daterange.from_date(
        first_day, period="quarter")


@pytest.mark.parametrize("quarter", [0, 5])
def test_from_quarter_value_check(quarter):
    with pytest.raises(ValueError):
        assert daterange.from_quarter(2000, quarter)


@pytest.mark.parametrize("year", [
    2000,
    2001,
])
def test_from_year(year):
    assert daterange.from_year(year) == daterange.from_date(
        date(year, 1, 1), period="year")


def test_last():
    span = daterange(date(2000, 1, 1), date(2000, 2, 1))
    assert span.last == date(2000, 1, 31)


def test_len_on_unbounded():
    with pytest.raises(ValueError):
        len(daterange())

    with pytest.raises(ValueError):
        len(daterange(date(2000, 1, 1)))

    with pytest.raises(ValueError):
        len(daterange(upper=date(2000, 1, 1)))


def test_bug5_date_subclassing():
    """
    `Bug #5 <https://github.com/runfalk/spans/issues/5>`
    """

    class DateSubClass(date):
        pass

    daterange(DateSubClass(2000, 1, 1))
