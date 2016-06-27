import pickle

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

        with self.assertRaises(TypeError):
            rset.add(floatrange(1.0))

    def test_remove(self):
        rset = intrangeset([intrange(upper=1), intrange(5)])
        rset.remove(intrange(10, 15))

        self.assertEqual(
            rset,
            intrangeset([intrange(upper=1), intrange(5, 10), intrange(15)]))

        # Test deletion of empty set
        temp = rset.copy()
        temp.remove(intrange.empty())
        self.assertEqual(rset, temp)

        # Test total deletion
        rset.remove(intrange())
        self.assertEqual(rset, intrangeset([]))

        # Test deletion on empty set
        temp = intrangeset([])
        temp.remove(intrange(1, 5))
        self.assertEqual(temp, intrangeset([]))

        with self.assertRaises(TypeError):
            rset.remove(floatrange(1.0))

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

        with self.assertRaises(TypeError):
            intrangeset().union(intrange())

    def test_difference(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(20, 30)]).difference(
                intrangeset([intrange(5, 10), intrange(20, 100)]))),
            [intrange(1, 5)])

        with self.assertRaises(TypeError):
            intrangeset().difference(intrange())

    def test_intersection(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(20, 30)]).intersection(
                intrangeset([intrange(5, 10), intrange(20, 100)]))),
            [intrange(20, 30)])
        self.assertFalse(
            intrangeset([intrange(1, 5)]).intersection(
                intrangeset([intrange(5, 10)])))

        with self.assertRaises(TypeError):
            intrangeset().intersection(intrange())

    def test_values(self):
        self.assertEqual(
            list(intrangeset([intrange(1, 5), intrange(10, 15)]).values()),
            list(range(1, 5)) + list(range(10, 15)))

    def test_repr(self):
        self.assertEqual(repr(intrangeset([])), "intrangeset([])")
        self.assertEqual(
            repr(intrangeset([intrange(1)])), "intrangeset([intrange([1,))])")

    def test_pickling(self):
        range = intrangeset([intrange(1, 10), intrange(20, 30)])

        self.assertEqual(range, pickle.loads(pickle.dumps(range)))

    def test_equal(self):
        range_a = intrange(1, 5)
        range_b = intrange(10, 15)

        self.assertTrue(
            intrangeset([range_a, range_b]) == intrangeset([range_a, range_b]))
        self.assertFalse(
            intrangeset([range_a, range_b]) == intrangeset([range_a]))
        self.assertFalse(
            intrangeset([range_a]) == "foo")

    def test_less_than(self):
        range_a = intrange(1, 5)
        range_b = intrange(10, 15)

        self.assertFalse(
            intrangeset([range_a, range_b]) < intrangeset([range_a]))
        self.assertTrue(
            intrangeset([range_a, range_b]) < intrangeset([range_b]))
        self.assertFalse(
            intrangeset([range_a, range_b]) <= intrangeset([range_a]))
        self.assertFalse(
            intrangeset([range_a]) == "foo")

    def test_greater_than(self):
        range_a = intrange(1, 5)
        range_b = intrange(10, 15)

        self.assertTrue(
            intrangeset([range_a, range_b]) > intrangeset([range_a]))
        self.assertFalse(
            intrangeset([range_a, range_b]) > intrangeset([range_b]))
        self.assertTrue(
            intrangeset([range_b]) > intrangeset([range_a, range_b]))
        self.assertTrue(
            intrangeset([range_a, range_b]) >= intrangeset([range_a]))
