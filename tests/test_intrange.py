import pytest

from spans import intrange

def test_len():
    assert len(intrange(0, 5)) == 5


def test_iter():
    assert list(intrange(0, 5)) == list(range(5))

    infinite_iter = iter(intrange(0))
    for i in range(100):
        assert i == next(infinite_iter)


def test_no_lower_bound_iter():
    with pytest.raises(TypeError):
        next(iter(intrange(upper=1)))


def test_reversed():
    assert list(reversed(intrange(0, 5))) == list(reversed(range(5)))

    infinite_iter = reversed(intrange(upper=100))
    for i in reversed(range(100)):
        assert i == next(infinite_iter)


def test_no_lower_upper_reversed():
    with pytest.raises(TypeError):
        next(reversed(intrange(1)))
