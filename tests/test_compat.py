import pytest
import sys

from spans._compat import fix_timedelta_repr


@pytest.mark.parametrize("original, patched", [
    ("timedelta(0)", "timedelta(0)"),
    ("timedelta(1)", "timedelta(days=1)"),
    ("timedelta(2)", "timedelta(days=2)"),
    ("timedelta(1, 2, 3)", "timedelta(days=1, seconds=2, microseconds=3)"),
    ("timedelta(0, 1)", "timedelta(seconds=1)"),
    ("timedelta(0, 0, 1)", "timedelta(microseconds=1)"),
    ("foobar", "foobar"),
])
def test_timedelta_repr_fix(original, patched):
    class Example(object):
        __doc__ = original

    if sys.version_info < (3, 7):
        # Ensure that docstrings are left as they are on version 3.6 and below
        assert fix_timedelta_repr(Example).__doc__ == original
    else:
        assert fix_timedelta_repr(Example).__doc__ == patched
