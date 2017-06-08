import pickle
import pytest

from spans import floatrange, floatrangeset, intrange, intrangeset


def test_empty():
    assert not intrangeset([])


def test_non_empty():
    assert intrangeset([intrange(1, 5)])


@pytest.mark.parametrize("rangeset, span", [
    (intrangeset([intrange(1, 5), intrange(10, 15)]), intrange(1, 15)),
    (intrangeset([]), intrange.empty()),
])
def test_span(rangeset, span):
    assert rangeset.span() == span


def test_iteration():
    ranges = [intrange(1, 5), intrange(10, 15)]
    assert list(intrangeset(ranges)) == ranges


def test_copy():
    rset = intrangeset([intrange(1, 5), intrange(10, 15)])
    rcopy = rset.copy()

    assert list(rset) == list(rcopy)
    assert rset._list is not rcopy._list


@pytest.mark.parametrize("value", [
    intrange(1, 5),
    intrange(5, 10),
    intrange.empty(),
    1,
    5,
])
def test_contains(value):
    assert intrangeset([intrange(1, 10)]).contains(value)


@pytest.mark.parametrize("value", [
    intrange(5, 15),
    10,
])
def test_not_contains(value):
    assert not intrangeset([intrange(1, 10)]).contains(value)


@pytest.mark.parametrize("rset", [
    intrangeset([]),
    intrangeset([intrange(1, 5)]),
])
def test_contains_empty(rset):
    assert rset.contains(intrange.empty())


def test_contains_type_check():
    with pytest.raises(ValueError):
        intrangeset([]).contains(1.0)

    with pytest.raises(ValueError):
        intrangeset([]).contains(floatrangeset([]))


def test_add():
    rset = intrangeset([intrange(1, 15)])
    rset.add(intrange(5, 15))

    assert list(rset) == [intrange(1, 15)]

    with pytest.raises(TypeError):
        rset.add(floatrange(1.0))


def test_remove():
    rset = intrangeset([intrange(upper=1), intrange(5)])
    rset.remove(intrange(10, 15))

    assert rset == intrangeset([intrange(upper=1), intrange(5, 10), intrange(15)])

    # Test deletion of empty set
    temp = rset.copy()
    temp.remove(intrange.empty())
    assert rset == temp

    # Test total deletion
    rset.remove(intrange())
    assert rset == intrangeset([])

    # Test deletion on empty set
    temp = intrangeset([])
    temp.remove(intrange(1, 5))
    assert temp == intrangeset([])

    with pytest.raises(TypeError):
        rset.remove(floatrange(1.0))


def test_invert():
    rset = intrangeset([intrange(1, 5), intrange(10, 15)])
    rset_inv = intrangeset([intrange(upper=1), intrange(5, 10), intrange(15)])

    assert ~rset == rset_inv
    assert rset == ~~rset


def test_union():
    a = intrangeset([intrange(1, 5), intrange(20, 30)])
    b = intrangeset([intrange(5, 10), intrange(20, 100)])
    union = [intrange(1, 10), intrange(20, 100)]

    assert list(a.union(b)) == union
    assert list(a | b) == union

    with pytest.raises(TypeError):
        intrangeset([]).union(intrange())
    assert intrangeset([]).__or__(intrange()) is NotImplemented


def test_difference():
    a = intrangeset([intrange(1, 5), intrange(20, 30)])
    b = intrangeset([intrange(5, 10), intrange(20, 100)])
    difference = [intrange(1, 5)]

    assert list(a.difference(b)) == difference
    assert list(a - b) == difference

    with pytest.raises(TypeError):
        intrangeset([]).difference(intrange())
    assert intrangeset([]).__sub__(intrange()) is NotImplemented


def test_intersection():
    a = intrangeset([intrange(1, 5), intrange(20, 30)])
    b = intrangeset([intrange(5, 10), intrange(20, 100)])
    intersection = [intrange(20, 30)]

    assert list(a.intersection(b)) == intersection
    assert list(a & b) == intersection
    assert not intrangeset([intrange(1, 5)]).intersection(
        intrangeset([intrange(5, 10)]))

    with pytest.raises(TypeError):
        intrangeset([]).intersection(intrange())
    assert intrangeset([]).__and__(intrange()) is NotImplemented


def test_values():
    values = intrangeset([intrange(1, 5), intrange(10, 15)]).values()
    assert list(values) == list(range(1, 5)) + list(range(10, 15))


@pytest.mark.parametrize("span, repr_str", [
    (intrangeset([]), "intrangeset([])"),
    (intrangeset([intrange(1)]), "intrangeset([intrange([1,))])"),
])
def test_repr(span, repr_str):
    assert repr(span) == repr_str


def test_pickling():
    span = intrangeset([intrange(1, 10), intrange(20, 30)])
    assert span == pickle.loads(pickle.dumps(span))


def test_equal():
    range_a = intrange(1, 5)
    range_b = intrange(10, 15)

    assert intrangeset([range_a, range_b]) == intrangeset([range_a, range_b])
    assert not intrangeset([range_a, range_b]) == intrangeset([range_a])
    assert not intrangeset([range_a]) == "foo"


def test_less_than():
    range_a = intrange(1, 5)
    range_b = intrange(10, 15)

    assert not intrangeset([range_a, range_b]) < intrangeset([range_a])
    assert intrangeset([range_a, range_b]) < intrangeset([range_b])
    assert not intrangeset([range_a, range_b]) <= intrangeset([range_a])
    assert not intrangeset([range_a]) == "foo"


def test_greater_than():
    range_a = intrange(1, 5)
    range_b = intrange(10, 15)

    assert intrangeset([range_a, range_b]) > intrangeset([range_a])
    assert not intrangeset([range_a, range_b]) > intrangeset([range_b])
    assert intrangeset([range_b]) > intrangeset([range_a, range_b])
    assert intrangeset([range_a, range_b]) >= intrangeset([range_a])


def test_bug3_intersection():
    """
    `Bug #3 <https://github.com/runfalk/spans/issues/3>`_
    """

    range_a = intrange(1, 5)
    range_b = intrange(5, 10)
    range_c = intrange(10, 15)

    rangeset_a = intrangeset([range_a, range_c])
    rangeset_b = intrangeset([range_b])
    rangeset_c = intrangeset([range_c])
    rangeset_empty = intrangeset([])

    assert rangeset_a.intersection(rangeset_b, rangeset_c) == rangeset_empty

def test_bug4_empty_set_iteration():
    """
    `Bug #4 <https://github.com/runfalk/spans/issues/4>`
    """

    assert list(intrangeset([])) == []
