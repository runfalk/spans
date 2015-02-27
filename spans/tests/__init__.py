import doctest
import imp
import os
import re
import sys
import unittest

from glob import iglob
from itertools import chain

from .._compat import python3

# Add unicode ignore functionality to doctest
IGNORE_UNICODE = doctest.register_optionflag("IGNORE_UNICODE")

class UnicodeIgnoreOutputChecker(doctest.OutputChecker):
    """
    Output checker for doctests that strips unicode literal prefixes from the
    expected output string. This is necessary for compatibility with both Python
    2 and 3. Example use:

        >>> u'Sample unicode string' # doctest: +IGNORE_UNICODE
        u'Sample unicode string'

    """

    _literal_re = re.compile(r"(\W|^)[uU]([rR]?[\'\"])", re.UNICODE)

    def check_output(self, want, got, optionflags):
        if optionflags & IGNORE_UNICODE and python3:
            want = re.sub(self._literal_re, r'\1\2', want)

        # OutputChecker seems to be an old style class so super() can't be used
        # for Python 2
        if python3:
            return super(UnicodeIgnoreOutputChecker, self).check_output(
                want, got, optionflags)
        else:
            return doctest.OutputChecker.check_output(
                self, want, got, optionflags)

def load_module(name, path):
    """Loads a module from the given path if it's not already loaded"""

    if sys.modules.get(name) is not None:
        return sys.modules[name]
    else:
        return imp.load_source(name, path)

def find_tests():
    for path in iglob(os.path.dirname(os.path.realpath(__file__)) + "/test_*.py"):
        name = os.path.basename(path)[:-3]
        yield unittest.defaultTestLoader.loadTestsFromModule(
            load_module(__name__ + "." + name, path))

def find_doctests():
    for path in iglob(os.path.dirname(os.path.realpath(__file__)) + "/../*.py"):
        name = os.path.basename(path)[:-3]
        yield doctest.DocTestSuite(
            load_module(".".join(__name__.split(".")[:-1]) + "." + name, path),
            checker=UnicodeIgnoreOutputChecker())

def suite():
    return unittest.TestSuite(chain(find_tests(), find_doctests()))

def main():
    runner = unittest.TextTestRunner(verbosity=1)
    return runner.run(suite())
