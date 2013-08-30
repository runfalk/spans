from unittest import TestCase

from ..types import *

class TestIntRange(TestCase):
    def test_empty(self):
        self.assertFalse(intrange.empty())

    def test_non_empty(self):
        self.assertTrue(intrange())

    def test_default_bounds(self):
        inf_range = intrange()
        self.assertFalse(inf_range.lower_inc)
        self.assertFalse(inf_range.upper_inc)

        bounded_range = intrange(1, 10)
        self.assertTrue(bounded_range.lower_inc)
        self.assertFalse(bounded_range.upper_inc)

        rebound_range =intrange().replace(lower=1, upper=10)
        self.assertTrue(rebound_range.lower_inc)
        self.assertFalse(rebound_range.upper_inc)

    def test_unbounded(self):
        range = intrange()

        self.assertIs(range.lower, None)
        self.assertIs(range.upper, None)

        self.assertTrue(range.lower_inf)
        self.assertTrue(range.upper_inf)

    def test_immutable(self):
        range = intrange()

        with self.assertRaises(AttributeError):
            range.lower = 1

        with self.assertRaises(AttributeError):
            range.upper = 10

        with self.assertRaises(AttributeError):
            range.lower_inc = True

        with self.assertRaises(AttributeError):
            range.upper_inc = True

    def test_equality(self):
        self.assertEqual(intrange(1, 5), intrange(1, 5))
        self.assertEqual(intrange.empty(), intrange.empty())
        self.assertNotEqual(intrange(1, 5), intrange(1, 5, upper_inc=True))

    def test_less_than(self):
        self.assertTrue(intrange(1, 5) < intrange(2, 5))
        self.assertTrue(intrange(1, 4) < intrange(1, 5))
        self.assertFalse(intrange(1, 5) < intrange(1, 5))
        self.assertTrue(intrange(1, 5) < intrange(1, 5, upper_inc=True))
        self.assertFalse(intrange(1, 5, lower_inc=False) < intrange(1, 5))

        self.assertTrue(intrange(1, 5) <= intrange(1, 5))
        self.assertTrue(intrange(1, 4) <= intrange(1, 5))
        self.assertFalse(intrange(2, 5) <= intrange(1, 5))

    def test_greater_than(self):
        self.assertTrue(intrange(2, 5) > intrange(1, 5))
        self.assertTrue(intrange(1, 5) > intrange(1, 4))
        self.assertFalse(intrange(1, 5) > intrange(1, 5))
        self.assertTrue(intrange(1, 5, upper_inc=True) > intrange(1, 5))
        self.assertTrue(intrange(1, 5, lower_inc=False) > intrange(1, 5))

        self.assertTrue(intrange(1, 5) >= intrange(1, 5))
        self.assertTrue(intrange(1, 5) >= intrange(1, 4))
        self.assertFalse(intrange(1, 5) >= intrange(2, 5))

    def test_left_of(self):
        self.assertTrue(intrange(1, 5).left_of(intrange(5, 10)))
        self.assertTrue(intrange(1, 5).left_of(intrange(10, 15)))
        self.assertFalse(intrange(1, 5, upper_inc=True).left_of(intrange(5, 10)))
        self.assertFalse(intrange(5, 10).left_of(intrange(1, 5)))

    def test_right_of(self):
        self.assertTrue(intrange(5, 10).right_of(intrange(1, 5)))
        self.assertTrue(intrange(5, 10).right_of(intrange(1, 5)))
        self.assertFalse(intrange(5, 10).right_of(intrange(1, 5, upper_inc=True)))
        self.assertFalse(intrange(1, 5).right_of(intrange(5, 10)))

    def test_startsafter(self):
        self.assertTrue(intrange(1, 5).startsafter(intrange(1, 5)))
        self.assertTrue(intrange(1, 5).startsafter(intrange(1, 10)))
        self.assertTrue(intrange(5, 10).startsafter(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).startsafter(intrange(5, 10)))
        self.assertFalse(
            intrange(1, 5).startsafter(intrange(1, 5, lower_inc=False)))

        # Test with infinities
        self.assertFalse(intrange(1, 10).startsafter(intrange(5)))
        self.assertTrue(intrange(1, 10).startsafter(intrange(upper=5)))

    def test_endsbefore(self):
        self.assertTrue(intrange(1, 5).endsbefore(intrange(1, 5)))
        self.assertTrue(intrange(5, 10).endsbefore(intrange(1, 10)))
        self.assertFalse(intrange(5, 10).endsbefore(intrange(1, 5)))
        self.assertFalse(intrange(5, 10).endsbefore(intrange(1, 5)))
        self.assertFalse(
            intrange(1, 5, upper_inc=True).endsbefore(intrange(1, 5)))

        # Test with infinities
        self.assertTrue(intrange(1, 10).endsbefore(intrange(5)))
        self.assertFalse(intrange(1, 10).endsbefore(intrange(upper=5)))

    def test_startswith(self):
        self.assertTrue(intrange(1, 5).startswith(intrange(1, 5)))
        self.assertTrue(intrange(1, 5).startswith(intrange(1, 10)))
        self.assertFalse(intrange(1, 5).startswith(intrange(5, 10)))
        self.assertFalse(intrange(5, 10).startswith(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).startswith(intrange(1, 5, lower_inc=False)))

        self.assertTrue(intrange(1, 5).startswith(1))
        self.assertFalse(intrange(1, 5, lower_inc=False).startswith(1))

    def test_endswith(self):
        self.assertTrue(intrange(5, 10).endswith(intrange(5, 10)))
        self.assertTrue(intrange(1, 10).endswith(intrange(5, 10)))
        self.assertFalse(intrange(1, 5).endswith(intrange(5, 10)))
        self.assertFalse(intrange(5, 10).endswith(intrange(1, 5)))
        self.assertFalse(intrange(1, 5, upper_inc=True).endswith(intrange(1, 5)))

        self.assertFalse(intrange(1, 5).endswith(5))
        self.assertTrue(intrange(1, 5, upper_inc=True).endswith(5))

    def test_contains(self):
        # Test ranges
        self.assertTrue(intrange(1, 5).contains(intrange(1, 5)))
        self.assertFalse(intrange(1, 5, lower_inc=False).contains(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).contains(intrange(1, 5, upper_inc=True)))
        self.assertTrue(intrange(1, 10).contains(intrange(1, 5)))
        self.assertTrue(intrange(1, 10).contains(intrange(5, 10)))

        # Test values
        self.assertTrue(intrange(1, 5).contains(1))
        self.assertTrue(intrange(1, 5).contains(3))
        self.assertFalse(intrange(1, 5, lower_inc=False).contains(1))
        self.assertFalse(intrange(1, 5).contains(5))

        with self.assertRaises(TypeError):
            intrange.contains(True)

    def test_within(self):
        # Test ranges
        self.assertTrue(intrange(1, 5).within(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).within(intrange(1, 5, lower_inc=False)))
        self.assertFalse(intrange(1, 5, upper_inc=True).within(intrange(1, 5)))
        self.assertTrue(intrange(1, 5).within(intrange(1, 10)))
        self.assertTrue(intrange(5, 10).within(intrange(1, 10)))

        with self.assertRaises(TypeError):
            intrange.within(True)

    def test_overlap(self):
        self.assertFalse(intrange(1, 5).overlap(intrange(5, 10)))
        self.assertTrue(intrange(1, 5, upper_inc=True).overlap(intrange(5, 10)))
        self.assertTrue(intrange(1, 5).overlap(intrange(3, 8)))
        self.assertTrue(intrange(3, 8).overlap(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).overlap(intrange(5, 10, lower_inc=False)))

        # Test infinities
        self.assertTrue(intrange(1, 10).overlap(intrange(5)))

    def test_adjacent(self):
        self.assertTrue(intrange(1, 5).adjacent(intrange(5, 10)))
        self.assertFalse(intrange(1, 5, upper_inc=True).adjacent(intrange(5, 10)))
        self.assertFalse(intrange(1, 5).adjacent(intrange(5, 10, lower_inc=False)))
        self.assertFalse(intrange(1, 5).adjacent(intrange(3, 8)))
        self.assertFalse(intrange(3, 8).adjacent(intrange(1, 5)))

    def test_union(self):
        self.assertEqual(intrange(1, 5).union(intrange(5, 10)), intrange(1, 10))
        self.assertEqual(intrange(1, 5).union(intrange(3, 10)), intrange(1, 10))
        self.assertEqual(intrange(5, 10).union(intrange(1, 5)), intrange(1, 10))
        self.assertEqual(intrange(3, 10).union(intrange(1, 5)), intrange(1, 10))

        with self.assertRaises(ValueError):
            intrange(1, 5).union(intrange(5, 10, lower_inc=False))

        with self.assertRaises(ValueError):
            intrange(5, 10, lower_inc=False).union(intrange(1, 5))

        with self.assertRaises(ValueError):
            intrange(10, 15).union(intrange(1, 5))

        with self.assertRaises(ValueError):
            intrange(1, 5).union(intrange(10, 15))

    def test_difference(self):
        self.assertEqual(intrange(1, 5).difference(intrange.empty()), intrange(1, 5))
        self.assertEqual(intrange(1, 5).difference(intrange(5, 10)), intrange(1, 5))
        self.assertEqual(intrange(1, 5).difference(intrange(3, 8)), intrange(1, 3))
        self.assertEqual(intrange(3, 8).difference(intrange(1, 5)), intrange(5, 8))
        self.assertEqual(
            intrange(3, 8).difference(intrange(1, 5, upper_inc=True)),
            intrange(5, 8, lower_inc=False))
        self.assertEqual(intrange(1, 5).difference(intrange(1, 3)), intrange(3, 5))
        self.assertEqual(intrange(1, 5).difference(intrange(3, 5)), intrange(1, 3))

        with self.assertRaises(ValueError):
            intrange(1, 15).difference(intrange(5, 10))

    def test_intersection(self):
        self.assertEqual(intrange(1, 5).intersection(intrange(1, 5)), intrange(1, 5))
        self.assertEqual(intrange(1, 15).intersection(intrange(5, 10)), intrange(5, 10))
        self.assertEqual(intrange(1, 5).intersection(intrange(3, 8)), intrange(3, 5))
        self.assertEqual(intrange(3, 8).intersection(intrange(1, 5)), intrange(3, 5))
        self.assertEqual(
            intrange(3, 8, lower_inc=False).intersection(intrange(1, 5)),
            intrange(3, 5, lower_inc=False))

        # Test something involving infinities
        self.assertEqual(intrange(1, 10).intersection(intrange(5)), intrange(5, 10))
        self.assertEqual(intrange(1, 10).intersection(intrange(upper=5)), intrange(1, 5))

