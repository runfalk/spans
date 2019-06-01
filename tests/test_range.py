import pickle
import pytest

from spans import (
    daterange,
    datetimerange,
    floatrange,
    intrange,
    PeriodRange,
    strrange,
    timedeltarange,
)
from spans.types import _Bound


def test_empty():
    empty_range = intrange.empty()

    assert not empty_range
    assert empty_range.lower is None
    assert empty_range.upper is None
    assert not empty_range.lower_inc
    assert not empty_range.upper_inc
    assert not empty_range.lower_inf
    assert not empty_range.upper_inf


def test_non_empty():
    assert intrange()


def test_bound_helper():
    # This is technically an implementation detail, but since it's used
    # everywhere it's good to exhaustively test it
    assert _Bound(1, inc=False, is_lower=False) < _Bound(1, inc=False, is_lower=True)
    assert _Bound(1, inc=False, is_lower=False) < _Bound(1, inc=True, is_lower=True)
    assert _Bound(1, inc=False, is_lower=False) < _Bound(1, inc=True, is_lower=False)

    assert _Bound(1, inc=False, is_lower=True) < _Bound(1, inc=True, is_lower=False)

    assert _Bound(1, inc=True, is_lower=False) < _Bound(1, inc=False, is_lower=True)

    assert _Bound(1, inc=True, is_lower=True) < _Bound(1, inc=True, is_lower=False)
    assert _Bound(1, inc=True, is_lower=True) < _Bound(1, inc=False, is_lower=True)


@pytest.mark.parametrize("range_type, lower, upper, lower_inc, upper_inc, exc_type", [
    (floatrange, 1, None, None, None, TypeError),
    (floatrange, None, 10, None, None, TypeError),
    (floatrange, 10.0, 1.0, None, None, ValueError),
    (floatrange, None, 10.0, True, None, ValueError),
    (floatrange, 10.0, None, None, True, ValueError),
    (intrange, 1.0, None, None, None, TypeError),
    (intrange, None, 10.0, None, None, TypeError),
    (intrange, 10, 1, None, None, ValueError),
    (intrange, None, 1, True, None, ValueError),
])
def test_invalid_construction(range_type, lower, upper, lower_inc, upper_inc, exc_type):
    with pytest.raises(exc_type):
        range_type(lower, upper, lower_inc, upper_inc)


@pytest.mark.parametrize("range_type, lower, upper", [
    (floatrange, 1.0, 10.0),
    (intrange, 1, 10),
])
def test_default_bounds(range_type, lower, upper):
    inf_range = range_type()
    assert not inf_range.lower_inc
    assert not inf_range.upper_inc

    bounded_range = range_type(lower, upper)
    assert bounded_range.lower_inc
    assert not bounded_range.upper_inc

    rebound_range = bounded_range.replace(lower, upper)
    assert rebound_range.lower_inc
    assert not rebound_range.upper_inc


def test_replace():
    span = floatrange(1.0, 10.0)
    assert span.lower_inc
    assert not span.upper_inc

    unbounded_span = span.replace(None)
    assert unbounded_span.lower_inf
    assert not unbounded_span.lower_inc
    assert not unbounded_span.upper_inf
    assert not unbounded_span.upper_inc

    # It's a bit confusing that the replace doesn't remember that the range
    # used to be lower_inc. However, we don't have a way of telling that the
    # value has not been user specified
    rebounded_span = unbounded_span.replace(lower=1.0)
    assert not rebounded_span.lower_inc


def test_unbounded():
    range = intrange()

    assert range.lower is None
    assert range.upper is None

    assert range.lower_inf
    assert range.upper_inf


@pytest.mark.parametrize("value, rep", [
    (floatrange(), "floatrange()"),
    (floatrange.empty(), "floatrange.empty()"),
    (floatrange(1.0), "floatrange(1.0)"),
    (floatrange(1.0, 10.0), "floatrange(1.0, 10.0)"),
    (floatrange(None, 1.0), "floatrange(upper=1.0)"),
    (floatrange(1.0, lower_inc=False), "floatrange(1.0, lower_inc=False)"),
    (floatrange(upper=10.0, upper_inc=True), "floatrange(upper=10.0, upper_inc=True)"),
    (intrange(1, 10), "intrange(1, 10)"),
])
def test_repr(value, rep):
    assert repr(value) == rep

def test_immutable():
    range = intrange()

    with pytest.raises(AttributeError):
        range.lower = 1

    with pytest.raises(AttributeError):
        range.upper = 10

    with pytest.raises(AttributeError):
        range.lower_inc = True

    with pytest.raises(AttributeError):
        range.upper_inc = True


def test_last():
    assert intrange().last is None
    assert intrange.empty().last is None
    assert intrange(1).last is None

    assert intrange(upper=10).last == 9
    assert intrange(1, 10).last == 9


def test_offset():
    low_range = intrange(0, 5)
    high_range = intrange(5, 10)

    assert low_range != high_range
    assert low_range.offset(5) == high_range
    assert low_range == high_range.offset(-5)

    with pytest.raises(TypeError):
        low_range.offset(5.0)


def test_offset_unbounded():
    range = intrange()
    assert range == range.offset(10)

    assert intrange(1).offset(9) == intrange(10)
    assert intrange(upper=1).offset(9) == intrange(upper=10)


def test_equality():
    assert intrange(1, 5) == intrange(1, 5)
    assert intrange.empty() == intrange.empty()
    assert intrange(1, 5) != intrange(1, 5, upper_inc=True)
    assert floatrange() == floatrange()
    assert not intrange() == None


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(2.0, 5.0)),
    (floatrange(1.0, 4.0), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0, upper_inc=True)),
    (floatrange(1.0, 5.0), floatrange(1.0)),
    (floatrange(upper=5.0), floatrange(1.0, 5.0)),
])
def test_less_than(a, b):
    assert a < b
    assert not b < a


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0)),
    (floatrange(1.0, 4.0), floatrange(1.0, 5.0)),
])
def test_less_equal(a, b):
    assert a <= b


@pytest.mark.parametrize("a, b", [
    (floatrange.empty(), floatrange.empty()),
    (floatrange.empty(), floatrange(1.0)),
    (floatrange(upper=-1.0), floatrange.empty()),
])
def test_empty_comparison(a, b):
    assert not a < b
    assert not a > b


@pytest.mark.parametrize("a, b", [
    (intrange(), floatrange()),
    (intrange(), None),
])
@pytest.mark.parametrize("op", [
    "__lt__",
    "__le__",
    "__gt__",
    "__ge__",
])
def test_comparison_operator_type_checks(a, b, op):
    # Hack used to work around version differences between Python 2 and 3
    # Python 2 has its own idea of how objects compare to each other.
    # Python 3 raises type error when an operation is not implemented
    assert getattr(a, op)(b) is NotImplemented


def test_greater_than():
    assert intrange(2, 5) > intrange(1, 5)
    assert intrange(1, 5) > intrange(1, 4)
    assert not intrange(1, 5) > intrange(1, 5)
    assert intrange(1, 5, upper_inc=True) > intrange(1, 5)
    assert intrange(1, 5, lower_inc=False) > intrange(1, 5)
    assert intrange(2) > intrange(1, 5)

    assert intrange(1, 5) >= intrange(1, 5)
    assert intrange(1, 5) >= intrange(1, 4)
    assert not intrange(1, 5) >= intrange(2, 5)

    # Hack used to work around version differences between Python 2 and 3.
    # Python 2 has its own idea of how objects compare to each other.
    # Python 3 raises type error when an operation is not implemented
    assert intrange().__gt__(floatrange()) is NotImplemented
    assert intrange().__ge__(floatrange()) is NotImplemented


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0, lower_inc=False), floatrange(5.0, 10.0, upper_inc=True)),
])
def test_left_or_right_of(a, b):
    assert a.left_of(b)
    assert a << b
    assert b.right_of(a)
    assert b >> a


@pytest.mark.parametrize("a, b", [
    (floatrange(5.0, 10.0), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0, upper_inc=True), floatrange(5.0, 10.0)),
    (floatrange.empty(), floatrange.empty()),
])
def test_not_left_or_right_of(a, b):
    assert not a.left_of(b)
    assert not (a << b)
    assert not b.right_of(a)
    assert not (b >> a)


def test_left_of_type_check():
    with pytest.raises(TypeError):
        floatrange().left_of(None)
    assert floatrange().__lshift__(None) is NotImplemented


def test_right_of_type_check():
    with pytest.raises(TypeError):
        floatrange().right_of(None)
    assert floatrange().__rshift__(None) is NotImplemented


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange(1.0, 10.0)),
    (floatrange(5.0, 10.0), floatrange(5.0, 10.0)),
    (floatrange(1.0, 10.0), floatrange(upper=5.0)),
    (floatrange(1.0, 5.0), 0.0),
])
def test_startsafter(a, b):
    assert a.startsafter(b)


@pytest.mark.parametrize("a, b", [
    (floatrange.empty(), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange.empty()),
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0, lower_inc=False)),
    (floatrange(1.0, 10.0), floatrange(5.0)),
    (floatrange.empty(), 1.0),
])
def test_not_startsafter(a, b):
    assert not a.startsafter(b)


def test_startsafter_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).startsafter(1.0)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0)),
    (floatrange(5.0, 10.0), floatrange(1.0, 10.0)),
    (floatrange(1.0, 10.0), floatrange(5.0)),
    (floatrange(1.0, 5.0), 5.0),
])
def test_endsbefore(a, b):
    assert a.endsbefore(b)


@pytest.mark.parametrize("a, b", [
    (floatrange.empty(), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange.empty()),
    (floatrange(5.0, 10.0), floatrange(1.0, 5.0)),
    (floatrange(5.0, 10.0), floatrange.empty()),
    (floatrange(1.0, 5.0, upper_inc=True), floatrange(1.0, 5.0)),
    (floatrange(1.0, 10.0), floatrange(upper=5.0)),
    (floatrange.empty(), 1.0),
])
def test_not_endsbefore(a, b):
    assert not a.endsbefore(b)


def test_endsbefore_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).endsbefore(1.0)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 10)),
    (intrange(1, 5), 1),
])
def test_startswith(a, b):
    assert a.startswith(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
    (intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 5, lower_inc=False)),
    (intrange(1, 5), 0),
])
def test_not_startswith(a, b):
    assert not a.startswith(b)


def test_startswith_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).startswith(5.0)


@pytest.mark.parametrize("a, b", [
    (intrange(5, 10), intrange(5, 10)),
    (intrange(1, 10), intrange(5, 10)),
    (intrange(1, 5, upper_inc=True), 5)
])
def test_startswith(a, b):
    assert a.endswith(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(5, 10)),
    (intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5, upper_inc=True), intrange(1, 5)),
    (intrange(1, 5), 5),
])
def test_not_endswith(a, b):
    assert not a.endswith(b)


def test_endswith_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).endswith(5.0)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0)),
    (floatrange(1.0, 10.0), floatrange(1.0, 5.0)),
    (floatrange(1.0, 10.0), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0), 1.0),
    (floatrange(1.0, 5.0), 3.0),
    (floatrange(1.0), 3.0),
    (floatrange(upper=5.0), 3.0),
])
def test_contains(a, b):
    assert a.contains(b)
    assert b in a


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0, lower_inc=False), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange(1.0, 5.0, upper_inc=True)),
    (floatrange(1.0, 5.0, lower_inc=False), 1.0),
    (floatrange(1.0, 5.0), 5.0),
    (floatrange(1.0, lower_inc=False), 1.0),
    (floatrange(upper=5.0), 5.0),
])
def test_not_contains(a, b):
    assert not a.contains(b)
    assert b not in a


def test_contains_type_check():
    with pytest.raises(TypeError):
        intrange(1, 5).contains(None)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5)),
    (intrange(1, 5), intrange(1, 10)),
    (intrange(5, 10), intrange(1, 10)),
])
def test_within(a, b):
    assert a.within(b)


@pytest.mark.parametrize("a, b", [
    (intrange(1, 5), intrange(1, 5, lower_inc=False)),
    (intrange(1, 5, upper_inc=True), intrange(1, 5)),
])
def test_not_within(a, b):
    assert not a.within(b)


@pytest.mark.parametrize("value", [
    True,
    None,
    1,
])
def test_within_type_check(value):
    with pytest.raises(TypeError):
        intrange(1, 5).within(value)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0, upper_inc=True), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0), floatrange(3.0, 8.0)),
    (floatrange(1.0, 10.0), floatrange(2.0, 8.0)),
    (floatrange(1.0, 10.0), floatrange(5.0)),
    (floatrange(upper=10.0), floatrange(1.0, 5.0)),
    (floatrange(1.0), floatrange()),
])
def test_overlap(a, b):
    assert a.overlap(b)
    assert b.overlap(a)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0, lower_inc=False)),
    (floatrange(upper=5.0), floatrange(5.0)),
])
def test_not_overlap(a, b):
    assert not a.overlap(b)
    assert not b.overlap(a)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0)),
])
def test_adjacent(a, b):
    assert a.adjacent(b)
    assert b.adjacent(a)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0, upper_inc=True), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0, lower_inc=False)),
    (floatrange(1.0, 5.0), floatrange(3.0, 8.0)),
    (floatrange(3.0, 8.0), floatrange(1.0, 5.0)),
    (floatrange.empty(), floatrange(0.0, 5.0)),
])
def test_not_adjacent(a, b):
    assert not a.adjacent(b)
    assert not b.adjacent(a)


@pytest.mark.parametrize("value", [
    None,
    1,
    floatrange(5.0, 10.0),
])
def test_adjacent_type_check(value):
    with pytest.raises(TypeError):
        intrange(1, 5).adjacent(value)


@pytest.mark.parametrize("a, b, union", [
    (floatrange.empty(), floatrange(5.0, 10.0), floatrange(5.0, 10.0)),
    (floatrange(1.0, 5.0), floatrange.empty(), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0), floatrange(1.0, 10.0)),
    (floatrange(1.0, 10.0), floatrange(5.0, 15.0), floatrange(1.0, 15.0)),
    (floatrange(1.0, 10.0, lower_inc=False), floatrange(5.0, 15.0), floatrange(1.0, 15.0, lower_inc=False)),
    (floatrange(1.0, 10.0), floatrange(5.0, 15.0, upper_inc=True), floatrange(1.0, 15.0, upper_inc=True)),
    (floatrange(10.0, 15.0), floatrange(1.0, 25.0), floatrange(1.0, 25.0)),
    (floatrange(0.0), floatrange(upper=10.0), floatrange()),
])
def test_union(a, b, union):
    assert a.union(b) == union
    assert b.union(a) == union
    assert a | b == union
    assert b | a == union


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, 5.0), floatrange(5.0, 10.0, lower_inc=False)),
    (floatrange(5.0, 10.0, lower_inc=False), floatrange(1.0, 5.0)),
    (floatrange(1.0, 5.0), floatrange(10.0, 15.0)),
])
def test_broken_union(a, b):
    with pytest.raises(ValueError):
        a.union(b)

    with pytest.raises(ValueError):
        b.union(a)

    with pytest.raises(ValueError):
        a | b

    with pytest.raises(ValueError):
        b | a


def test_union_typecheck():
    a = floatrange(1.0, 5.0)
    b = intrange(5, 10)

    with pytest.raises(TypeError):
        a.union(b)
    assert a.__or__(b) is NotImplemented

@pytest.mark.parametrize("a, b, difference", [
    (intrange(1, 5), intrange.empty(), intrange(1, 5)),
    (intrange(1, 5), intrange(5, 10), intrange(1, 5)),
    (intrange(1, 5), intrange(3, 8), intrange(1, 3)),
    (intrange(3, 8), intrange(1, 5), intrange(5, 8)),
    (intrange(3, 8), intrange(1, 5, upper_inc=True), intrange(5, 8, lower_inc=False)),
    (intrange(1, 5), intrange(1, 3), intrange(3, 5)),
    (intrange(1, 5), intrange(3, 5), intrange(1, 3)),
    (intrange(1, 5), intrange(1, 10), intrange.empty()),
])
def test_difference(a, b, difference):
    assert a.difference(b) == difference
    assert a - b == difference


def test_broken_difference():
    with pytest.raises(ValueError):
        intrange(1, 15).difference(intrange(5, 10))

    with pytest.raises(ValueError):
        intrange(1, 15) - intrange(5, 10)


def test_difference_typecheck():
    a = floatrange(1.0, 10.0)
    b = intrange(5, 10)

    with pytest.raises(TypeError):
        a.difference(b)
    assert a.__sub__(b) is NotImplemented


@pytest.mark.parametrize("a, b, intersection", [
    (intrange(1, 5), intrange(1, 5), intrange(1, 5)),
    (intrange(1, 15), intrange(5, 10), intrange(5, 10)),
    (intrange(1, 5), intrange(3, 8), intrange(3, 5)),
    (intrange(3, 8), intrange(1, 5), intrange(3, 5)),
    (intrange(3, 8, lower_inc=False), intrange(1, 5), intrange(3, 5, lower_inc=False)),
    (intrange(1, 10), intrange(5), intrange(5, 10)),
    (intrange(1, 10), intrange(upper=5), intrange(1, 5)),
])
def test_intersection(a, b, intersection):
    assert a.intersection(b) == intersection
    assert b.intersection(a) == intersection
    assert a & b == intersection
    assert b & a == intersection


def test_intersection_typecheck():
    a = floatrange(1.0, 5.0)
    b = intrange(5, 10)

    with pytest.raises(TypeError):
        a.intersection(b)
    assert a.__and__(b) is NotImplemented


def test_pickling():
    span = intrange(1, 10)
    assert span == pickle.loads(pickle.dumps(span))


def test_bug7_overlap_empty():
    assert not intrange(1, 10).overlap(intrange.empty())


@pytest.mark.parametrize("cls", [
    daterange,
    datetimerange,
    intrange,
    floatrange,
    PeriodRange,
    strrange,
    timedeltarange,
])
def test_bug10_missing_slots_in_cls_hierarchy(cls):
    """
    `Bug #10 <https://github.com/runfalk/spans/issues/10>`_
    """

    for c in cls.mro():
        if c is object:
            continue
        assert hasattr(c, "__slots__")

def test_bug11_valid_union_call_detected_as_invalid():
    """
    `Bug #11 <https://github.com/runfalk/spans/issues/11>`_
    """
    start, middle, end = 0.0, 1.0, 2.0
    a = floatrange(start, middle, upper_inc=True)
    b = floatrange(middle, end)

    assert a.union(b) == floatrange(start, end)
