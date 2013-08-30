import doctest
import os
import imp
import unittest
import sys

from glob import iglob
from itertools import chain

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
            load_module(".".join(__name__.split(".")[:-1]) + "." + name, path))

def suite():
    return unittest.TestSuite(chain(find_tests(), find_doctests()))

def main():
    runner = unittest.TextTestRunner(verbosity=1)
    return runner.run(suite())
