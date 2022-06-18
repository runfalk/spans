import sys

import pytest

from spans import strrange
from spans._compat import uchr


@pytest.mark.parametrize(
    "span, last",
    [
        (strrange("a", "c"), "b"),
        (strrange("aa", "cc"), "cb"),
    ],
)
def test_last(span, last):
    assert span.last == last


@pytest.mark.parametrize(
    "a, b",
    [
        ("", ""),
        ("b", "a"),
        (uchr(0), uchr(sys.maxunicode)),
    ],
)
def test_prev(a, b):
    assert strrange.prev(a) == b


@pytest.mark.parametrize(
    "a, b",
    [
        ("", ""),
        ("a", "b"),
        (uchr(sys.maxunicode), uchr(0)),
    ],
)
def test_next(a, b):
    assert strrange.next(a) == b
