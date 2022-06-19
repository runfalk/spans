import sys

import pytest

from spans import strrange


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
        (chr(0), chr(sys.maxunicode)),
    ],
)
def test_prev(a, b):
    assert strrange.prev(a) == b


@pytest.mark.parametrize(
    "a, b",
    [
        ("", ""),
        ("a", "b"),
        (chr(sys.maxunicode), chr(0)),
    ],
)
def test_next(a, b):
    assert strrange.next(a) == b
