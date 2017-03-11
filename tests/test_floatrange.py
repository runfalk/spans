import pytest

from spans import floatrange


@pytest.mark.parametrize("lower, upper", [
    ("foo", None),
    (None, "foo"),
])
def test_type_check(lower, upper):
    with pytest.raises(TypeError):
        floatrange(lower, upper)


@pytest.mark.parametrize("lower, upper", [
    (10.0, 5.0),
])
def test_invalid_bounds(lower, upper):
    with pytest.raises(ValueError):
        floatrange(lower, upper)


def test_less_than():
    # Special case that discrete ranges can't cover
    assert floatrange(1.0) < floatrange(1.0, lower_inc=False)
    assert not floatrange(1.0, lower_inc=False) < floatrange(1.0)


@pytest.mark.parametrize("span, value", [
    (floatrange(1.0, 5.0), 1.0),
    (floatrange(1.0, 5.0), 3.0),
    (floatrange(1.0, 5.0, upper_inc=True), 5.0),
    (floatrange(1.0, 5.0, lower_inc=False, upper_inc=True), 5.0),
])
def test_contains(span, value):
    assert span.contains(value)


@pytest.mark.parametrize("span, value", [
    (floatrange(1.0, 5.0, lower_inc=False), 1.0),
    (floatrange(1.0, 5.0), 5.0),
])
def test_not_contains(span, value):
    assert not span.contains(value)


@pytest.mark.parametrize("a, b", [
    (floatrange(1.0, lower_inc=False), 1.0),
    (floatrange(1.0, lower_inc=False), floatrange(1.0)),
])
def test_startswith(a, b):
    # Special case that discrete ranges can't cover
    assert not a.startswith(b)


def test_endswith():
    # Special case that discrete ranges can't cover
    assert floatrange(upper=5.0, upper_inc=True).endswith(5.0)


@pytest.mark.parametrize("a, b", [
    (floatrange(upper=5.0), 5.0),
    (floatrange(upper=5.0), floatrange(upper=5.0, upper_inc=True)),
])
def test_not_endswith(a, b):
    # Special case that discrete ranges can't cover
    assert not a.endswith(b)
