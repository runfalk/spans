import pytest
import sys

from spans import strrange
from spans._compat import uchr

@pytest.mark.parametrize("span, last", [
    (strrange(u"a", u"c"), u"b"),
    (strrange(u"aa", u"cc"), u"cb"),
])
def test_last(span, last):
    assert span.last == last


@pytest.mark.parametrize("a, b", [
    (u"", u""),
    (u"b", u"a"),
    (uchr(0), uchr(sys.maxunicode)),
])
def test_prev(a, b):
    assert strrange.prev(a) == b


@pytest.mark.parametrize("a, b", [
    (u"", u""),
    (u"a", u"b"),
    (uchr(sys.maxunicode), uchr(0)),
])
def test_next(a, b):
    assert strrange.next(a) == b
