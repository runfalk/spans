import pytest

from spans import intrange

@pytest.mark.parametrize("a, offset, b", [
    (intrange(0), 5, intrange(5)),
    (intrange(upper=0), 5, intrange(upper=5)),
    (intrange(0, 5), 5, intrange(5, 10)),
    (intrange(), 5, intrange()),
])
def test_offset(a, offset, b):
    assert a.offset(offset) == b
