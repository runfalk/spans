import pickle
import sys

from datetime import date, datetime, timedelta
from unittest import TestCase

from .._compat import uchr
from ..types import *

class TestIntRange(TestCase):
    def test_empty(self):
        range = intrange.empty()

        self.assertFalse(range)

        self.assertIsNone(range.lower)
        self.assertIsNone(range.upper)

    def test_non_empty(self):
        self.assertTrue(intrange())

    def test_default_bounds(self):
        inf_range = intrange()
        self.assertFalse(inf_range.lower_inc)
        self.assertFalse(inf_range.upper_inc)

        bounded_range = intrange(1, 10)
        self.assertTrue(bounded_range.lower_inc)
        self.assertFalse(bounded_range.upper_inc)

        rebound_range = intrange().replace(lower=1, upper=10)
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

    def test_last(self):
        self.assertIsNone(intrange().last)
        self.assertIsNone(intrange.empty().last)
        self.assertIsNone(intrange(1).last)

        self.assertEqual(intrange(upper=10).last, 9)
        self.assertEqual(intrange(1, 10).last, 9)

    def test_offset(self):
        low_range = intrange(0, 5)
        high_range = intrange(5, 10)

        self.assertNotEqual(low_range, high_range)
        self.assertEqual(low_range.offset(5), high_range)
        self.assertEqual(low_range, high_range.offset(-5))

        with self.assertRaises(TypeError):
            low_range.offset(5.0)

    def test_offset_unbounded(self):
        range = intrange()

        self.assertEqual(range, range.offset(10))

    def test_equality(self):
        self.assertEqual(intrange(1, 5), intrange(1, 5))
        self.assertEqual(intrange.empty(), intrange.empty())
        self.assertNotEqual(intrange(1, 5), intrange(1, 5, upper_inc=True))

        self.assertFalse(intrange() == None)

    def test_less_than(self):
        self.assertTrue(intrange(1, 5) < intrange(2, 5))
        self.assertTrue(intrange(1, 4) < intrange(1, 5))
        self.assertFalse(intrange(1, 5) < intrange(1, 5))
        self.assertTrue(intrange(1, 5) < intrange(1, 5, upper_inc=True))
        self.assertFalse(intrange(1, 5, lower_inc=False) < intrange(1, 5))

        self.assertTrue(intrange(1, 5) <= intrange(1, 5))
        self.assertTrue(intrange(1, 4) <= intrange(1, 5))
        self.assertFalse(intrange(2, 5) <= intrange(1, 5))

        # Hack used to work around version differences between Python 2 and 3
        # Python 2 has its own idea of how objects compare to each other.
        # Python 3 raises type error when an operation is not implemented
        self.assertIs(intrange().__lt__(floatrange()), NotImplemented)
        self.assertIs(intrange().__le__(floatrange()), NotImplemented)

    def test_greater_than(self):
        self.assertTrue(intrange(2, 5) > intrange(1, 5))
        self.assertTrue(intrange(1, 5) > intrange(1, 4))
        self.assertFalse(intrange(1, 5) > intrange(1, 5))
        self.assertTrue(intrange(1, 5, upper_inc=True) > intrange(1, 5))
        self.assertTrue(intrange(1, 5, lower_inc=False) > intrange(1, 5))

        self.assertTrue(intrange(1, 5) >= intrange(1, 5))
        self.assertTrue(intrange(1, 5) >= intrange(1, 4))
        self.assertFalse(intrange(1, 5) >= intrange(2, 5))

        # Hack used to work around version differences between Python 2 and 3.
        # Python 2 has its own idea of how objects compare to each other.
        # Python 3 raises type error when an operation is not implemented
        self.assertIs(intrange().__gt__(floatrange()), NotImplemented)
        self.assertIs(intrange().__ge__(floatrange()), NotImplemented)

    def test_left_of(self):
        self.assertTrue(intrange(1, 5).left_of(intrange(5, 10)))
        self.assertTrue(intrange(1, 5).left_of(intrange(10, 15)))
        self.assertFalse(intrange(1, 5, upper_inc=True).left_of(intrange(5, 10)))
        self.assertFalse(intrange(5, 10).left_of(intrange(1, 5)))

        self.assertFalse(intrange.empty().left_of(intrange.empty()))

    def test_right_of(self):
        self.assertTrue(intrange(5, 10).right_of(intrange(1, 5)))
        self.assertTrue(intrange(5, 10).right_of(intrange(1, 5)))
        self.assertFalse(intrange(5, 10).right_of(intrange(1, 5, upper_inc=True)))
        self.assertFalse(intrange(1, 5).right_of(intrange(5, 10)))

        self.assertFalse(intrange.empty().right_of(intrange.empty()))

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

        self.assertTrue(intrange(1, 5).startsafter(0))

        with self.assertRaises(TypeError):
            intrange(1, 5).startsafter(1.0)

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

        self.assertTrue(intrange(1, 5).endsbefore(5))

        with self.assertRaises(TypeError):
            intrange(1, 5).endsbefore(5.0)

    def test_startswith(self):
        self.assertTrue(intrange(1, 5).startswith(intrange(1, 5)))
        self.assertTrue(intrange(1, 5).startswith(intrange(1, 10)))
        self.assertFalse(intrange(1, 5).startswith(intrange(5, 10)))
        self.assertFalse(intrange(5, 10).startswith(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).startswith(intrange(1, 5, lower_inc=False)))

        self.assertTrue(intrange(1, 5).startswith(1))
        self.assertFalse(intrange(1, 5, lower_inc=False).startswith(1))

        with self.assertRaises(TypeError):
            intrange(1, 5).startswith(1.0)

    def test_endswith(self):
        self.assertTrue(intrange(5, 10).endswith(intrange(5, 10)))
        self.assertTrue(intrange(1, 10).endswith(intrange(5, 10)))
        self.assertFalse(intrange(1, 5).endswith(intrange(5, 10)))
        self.assertFalse(intrange(5, 10).endswith(intrange(1, 5)))
        self.assertFalse(intrange(1, 5, upper_inc=True).endswith(intrange(1, 5)))

        self.assertFalse(intrange(1, 5).endswith(5))
        self.assertTrue(intrange(1, 5, upper_inc=True).endswith(5))

        with self.assertRaises(TypeError):
            intrange(1, 5).endswith(5.0)

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
            intrange(1, 5).contains(None)

    def test_within(self):
        # Test ranges
        self.assertTrue(intrange(1, 5).within(intrange(1, 5)))
        self.assertFalse(intrange(1, 5).within(intrange(1, 5, lower_inc=False)))
        self.assertFalse(intrange(1, 5, upper_inc=True).within(intrange(1, 5)))
        self.assertTrue(intrange(1, 5).within(intrange(1, 10)))
        self.assertTrue(intrange(5, 10).within(intrange(1, 10)))

        with self.assertRaises(TypeError):
            intrange(1, 5).within(1)

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

        # Test that empty range is not adjacent to a range
        self.assertFalse(intrange.empty().adjacent(intrange(0, 5)))

        with self.assertRaises(TypeError):
            intrange(1, 5).adjacent(floatrange(5.0, 10.0))

    def test_union(self):
        self.assertEqual(intrange(1, 5).union(intrange(5, 10)), intrange(1, 10))
        self.assertEqual(intrange(1, 5).union(intrange(3, 10)), intrange(1, 10))
        self.assertEqual(intrange(5, 10).union(intrange(1, 5)), intrange(1, 10))
        self.assertEqual(intrange(3, 10).union(intrange(1, 5)), intrange(1, 10))

        # Test interaction with empty ranges
        self.assertEqual(intrange.empty().union(intrange(1, 5)), intrange(1, 5))
        self.assertEqual(intrange(1, 5).union(intrange.empty()), intrange(1, 5))

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
        self.assertEqual(intrange(1, 5).difference(intrange(1, 10)), intrange.empty())

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

    def test_pickling(self):
        range = intrange(1, 10)

        self.assertEqual(range, pickle.loads(pickle.dumps(range)))

    def test_iteration(self):
        self.assertEqual(list(intrange(1, 10)), list(range(1, 10)))

class TestFloatRange(TestCase):
    def test_invalid_bounds(self):
        with self.assertRaises(TypeError):
            intrange("foo")

        with self.assertRaises(TypeError):
            intrange(upper="foo")

        with self.assertRaises(ValueError):
            floatrange(10.0, 5.0)

    def test_less_than(self):
        # Special case that discrete ranges can't cover
        self.assertTrue(floatrange(1.0) < floatrange(1.0, lower_inc=False))
        self.assertFalse(floatrange(1.0, lower_inc=False) < floatrange(1.0))

    def test_contains(self):
        self.assertTrue(floatrange(1.0, 5.0).contains(1.0))
        self.assertTrue(floatrange(1.0, 5.0).contains(3.0))
        self.assertFalse(floatrange(1.0, 5.0, lower_inc=False).contains(1.0))
        self.assertTrue(
            floatrange(1.0, 5.0, upper_inc=True).contains(5.0))
        self.assertTrue(
            floatrange(1.0, 5.0, lower_inc=False, upper_inc=True).contains(5.0))
        self.assertFalse(floatrange(1.0, 5.0).contains(5.0))

    def test_startswith(self):
        # Special case that discrete ranges can't cover
        self.assertFalse(floatrange(1.0, lower_inc=False).startswith(1.0))
        self.assertFalse(floatrange(1.0, lower_inc=False).startswith(
            floatrange(1.0)))

    def test_endswith(self):
        # Special case that discrete ranges can't cover
        self.assertFalse(floatrange(upper=5.0).endswith(5.0))
        self.assertTrue(floatrange(upper=5.0, upper_inc=True).endswith(5.0))

        self.assertFalse(floatrange(upper=5.0).endswith(
            floatrange(upper=5.0, upper_inc=True)))

class TestDateRange(TestCase):
    def test_datetime(self):
        with self.assertRaises(TypeError):
            daterange(datetime(2000, 1, 1))

        with self.assertRaises(TypeError):
            daterange(upper=datetime(2000, 1, 1))

    def test_offset(self):
        range_low = daterange(date(2000, 1, 1), date(2000, 1, 6))
        range_high = daterange(date(2000, 1, 5), date(2000, 1, 10))

        self.assertNotEqual(range_low, range_high)
        self.assertEqual(range_low.offset(timedelta(days=4)), range_high)
        self.assertEqual(range_low, range_high.offset(timedelta(days=-4)))

    def test_from_date(self):
        date_start = date(2000, 1, 1)
        self.assertEqual(
            daterange.from_date(date_start),
            daterange(date_start, date_start + timedelta(1)))

        with self.assertRaises(TypeError):
            daterange.from_date(datetime(2000, 1, 1))

    def test_last(self):
        span = daterange(date(2000, 1, 1), date(2000, 2, 1))
        self.assertEqual(span.last, date(2000, 1, 31))

    def test_datetime_input(self):
        with self.assertRaises(TypeError):
            daterange(datetime(2000, 1, 1))

    def test_len(self):
        with self.assertRaises(ValueError):
            len(daterange())


class TestStrRange(TestCase):
    def test_last(self):
        self.assertEqual(strrange(u"a", u"c").last, u"b")
        self.assertEqual(strrange(u"aa", u"cc").last, u"cb")

    def test_prev(self):
        self.assertEqual(strrange.prev(u""), u"")
        self.assertEqual(strrange.prev(u"b"), u"a")

        # Confirm that wrap around is correct
        self.assertEqual(strrange.prev(uchr(0)), uchr(sys.maxunicode))

    def test_next(self):
        self.assertEqual(strrange.next(u""), u"")
        self.assertEqual(strrange.next(u"a"), u"b")

        # Confirm that wrap around is correct
        self.assertEqual(strrange.next(uchr(sys.maxunicode)), uchr(0))
