import pickle
import pytest

from spans import \
    daterangeset, datetimerangeset, floatrange, floatrangeset, intrange, \
    intrangeset, strrangeset, timedeltarangeset


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
    (intrangeset([intrange(1)]), "intrangeset([intrange(1)])"),
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
    `Bug #4 <https://github.com/runfalk/spans/issues/4>`_
    """

    assert list(intrangeset([])) == []


@pytest.mark.parametrize("cls", [
    daterangeset,
    datetimerangeset,
    intrangeset,
    floatrangeset,
    strrangeset,
    timedeltarangeset,
])
def test_bug10_missing_slots_in_cls_hierarchy(cls):
    """
    `Bug #10 <https://github.com/runfalk/spans/issues/10`_
    """

    for c in cls.mro():
        if c is object:
            continue
        assert hasattr(c, "__slots__")


def test_bug14_pickle_not_working_for_rangesets():
    """
    `Bug #14 <https://github.com/runfalk/spans/issues/14`_
    """
    # If __getstate__ returns a falsy value __setstate__ will not be called
    # when loading the value again, which is why this bug occured
    range_set = floatrangeset([])
    pickled = pickle.dumps(range_set, protocol=1)
    pickle.loads(pickled)
    assert range_set == pickle.loads(pickled)

    # We need to ensure that code pickled using protocol 1 by spans versions
    # before 1.1.0 still loads
    old_data = (
        b"ccopy_reg\n_reconstructor\nq\x00(cspans.settypes\nfloatrangeset\n"
        b"q\x01c__builtin__\nobject\nq\x02Ntq\x03Rq\x04]q\x05h\x00(cspans."
        b"types\nfloatrange\nq\x06h\x02Ntq\x07Rq\x08}q\tX\x06\x00\x00\x00_"
        b"rangeq\nh\x00(cspans.types\n_internal_range\nq\x0bc__builtin__\n"
        b"tuple\nq\x0c(G?\xf0\x00\x00\x00\x00\x00\x00NI01\nI00\nI00\ntq\rtq"
        b"\x0eRq\x0fsbab."
    )
    assert pickle.loads(old_data) == floatrangeset([floatrange(1.0)])
