"""Compatibility module for python 3"""

import sys

__all__ = ["python3", "version", "bstr", "ustr", "uchr", "u_doctest"]

version = tuple(map(int, sys.version.split(" ")[0].split(".")))
python3 = False

if version >= (3, 0, 0):
    python3 = True

    if version < (3, 3, 0):
        raise ImportError("Module is only compatible with Python (<=2.7, >=3.3)")

    bstr, ustr, uchr = bytes, str, chr
else:
    bstr, ustr, uchr = str, unicode, unichr

def u_doctest(string):
    return string.replace("{u}", "" if python3 else "u")
