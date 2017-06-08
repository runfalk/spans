import pytest

from spans import intrange

def test_len():
    assert len(intrange(0, 5)) == 5
