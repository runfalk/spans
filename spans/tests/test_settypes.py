from unittest import TestCase

from ..types import *
from ..settypes import *

class TestIntRangeSet(TestCase):
    def test_empty(self):
        self.assertFalse(intrangeset([]))

    def test_nonempty(self):
        self.assertTrue(intrangeset([intrange(1, 5)]))

    def test_span(self):
        self.assertEqual(
            intrangeset([intrange(1, 5), intrange(10, 15)]).span(),
            intrange(1, 15))
        self.assertEqual(intrangeset([]).span(), intrange.empty())

    def test_iteration(self):
        ranges = [intrange(1, 5), intrange(10, 15)]
        self.assertEqual(list(intrangeset(ranges)), ranges)

    def test_copy(self):
        rset = intrangeset([intrange(1, 5), intrange(10, 15)])
        rcopy = rset.copy()

        self.assertEqual(list(rset), list(rcopy))
        self.assertIsNot(rset._list, rcopy._list)

    def test_add(self):
        rset = intrangeset([intrange(1, 15)])
        rset.add(intrange(5, 15))

        self.assertEqual(list(rset), [intrange(1, 15)])

    def test_remove(self):
        rset = intrangeset([intrange(upper=1), intrange(5)])
        rset.remove(intrange(10, 15))

        self.assertEqual(
            rset,
            intrangeset([intrange(upper=1), intrange(5, 10), intrange(15)]))

    def test_invert(self):
        rset = intrangeset([intrange(1, 5), intrange(10, 15)])
        rset_inv = intrangeset([intrange(upper=1), intrange(5, 10), intrange(15)])

        self.assertEqual(~rset, rset_inv)
        self.assertEqual(rset, ~~rset)

    def test_union(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(20, 30)]).union(
                intrangeset([intrange(5, 10), intrange(20, 100)]))),
            [intrange(1, 10), intrange(20, 100)])

    def test_difference(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(20, 30)]).difference(
                intrangeset([intrange(5, 10), intrange(20, 100)]))),
            [intrange(1, 5)])

    def test_intersection(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(20, 30)]).intersection(
                intrangeset([intrange(5, 10), intrange(20, 100)]))),
            [intrange(20, 30)])
        self.assertFalse(
            intrangeset([intrange(1, 5)]).intersection(
                intrangeset([intrange(5, 10)])))

    def test_values(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(10, 15)]).values()),
            list(range(1, 5)) + list(range(10, 15)))
