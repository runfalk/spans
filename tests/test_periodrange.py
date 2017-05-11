import pytest

from datetime import date
from spans import daterange, PeriodRange


@pytest.mark.parametrize("period", [
    "day",
    "week",
    "american_week",
    "month",
    "quarter",
    "year",
])
def test_type(period):
    span = PeriodRange.from_date(date(2000, 1, 1), period=period)
    assert span.period == period


def test_empty_type_error():
    with pytest.raises(TypeError):
        PeriodRange.empty()


def test_daterange_property():
    daterange_span = daterange.from_date(date(2000, 1, 1), period="month")
    span = PeriodRange.from_date(date(2000, 1, 1), period="month")

    assert type(span.daterange) is daterange
    assert daterange_span == span.daterange


def test_daterange_subclass():
    assert issubclass(PeriodRange, daterange)


def test_replace():
    span_2000 = PeriodRange.from_year(2000)
    span = span_2000.replace(upper=date(2002, 1, 1))

    daterange_2000 = daterange.from_year(2000)
    daterange_2001 = daterange.from_year(2001)
    daterange_span = daterange_2000.union(daterange_2001)

    assert type(span) is type(daterange_span)
    assert span == daterange_span


@pytest.mark.parametrize("range_type_a, range_type_b", [
    (PeriodRange, PeriodRange),
    (daterange, PeriodRange),
    (PeriodRange, daterange),
])
def test_union(range_type_a, range_type_b):
    span_2000 = range_type_a.from_year(2000)
    span_2001 = range_type_b.from_year(2001)

    span = span_2000.union(span_2001)

    assert span.lower == date(2000, 1, 1)
    assert span.upper == date(2002, 1, 1)
    assert type(span) is daterange


@pytest.mark.parametrize("range_type_a, range_type_b", [
    (PeriodRange, PeriodRange),
    (daterange, PeriodRange),
    (PeriodRange, daterange),
])
def test_intersection(range_type_a, range_type_b):
    span_a = range_type_a.from_week(2000, 1)
    span_b = range_type_b.from_month(2000, 1)

    span = span_a.intersection(span_b)

    assert span.lower == date(2000, 1, 3)
    assert span.upper == date(2000, 1, 10)
    assert type(span) is daterange


@pytest.mark.parametrize("range_type_a, range_type_b", [
    (PeriodRange, PeriodRange),
    (daterange, PeriodRange),
    (PeriodRange, daterange),
])
def test_difference(range_type_a, range_type_b):
    span_a = range_type_a.from_quarter(2000, 1)
    span_b = range_type_b.from_month(2000, 1)

    span = span_a.difference(span_b)

    assert span.lower == date(2000, 2, 1)
    assert span.upper == date(2000, 4, 1)
    assert type(span) is daterange


@pytest.mark.parametrize("a, b", [
    (PeriodRange.from_week(1999, 52), PeriodRange.from_week(2000, 1)),
    (PeriodRange.from_week(2000, 1), PeriodRange.from_week(2000, 2)),
    (PeriodRange.from_week(2009, 53), PeriodRange.from_week(2010, 1)),
])
def test_prev_next_period(a, b):
    assert a.next_period() == b
    assert a == b.prev_period()


@pytest.mark.parametrize("a, offset, b", [
    (PeriodRange.from_week(2000, 1), 52, PeriodRange.from_week(2001, 1)),
    (PeriodRange.from_month(2000, 1), 12, PeriodRange.from_month(2001, 1)),
    (PeriodRange.from_quarter(2000, 1), 4, PeriodRange.from_quarter(2001, 1)),
    (PeriodRange.from_year(2000), 10, PeriodRange.from_year(2010)),
])
def test_offset(a, offset, b):
    assert a.offset(offset) == b
    assert a == b.offset(-offset)


def test_zero_offset():
    period = PeriodRange.from_week(2000, 1)
    assert period.offset(0) is period
