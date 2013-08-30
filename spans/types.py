import sys

from collections import namedtuple
from datetime import date, datetime, timedelta
from functools import total_ordering

from ._compat import *

__all__ = [
    "intrange",
    "floatrange",
    "strrange",
    "daterange",
    "datetimerange",
    "timedeltarange"
]

_internal_range = namedtuple(
    "internal_range", ["lower", "upper", "lower_inc", "upper_inc", "empty"])
_empty_internal_range = _internal_range(None, None, False, False, True)

@total_ordering
class range_(object):
    """Base class of all ranges."""

    __slots__ = ("_range")

    def __init__(self, lower=None, upper=None, lower_inc=True, upper_inc=False):
        """
        Initialize a new range object. This is very strict about types. It allows
        subclasses but nothing else. None as lower or upper boundary means
        -infinity or infinity.
        """

        if lower is not None and not isinstance(lower, self.type):
            raise TypeError((
                "Invalid type for lower bound '{lower_type.__name__}'"
                " expected '{expected_type.__name__}'").format(
                    expected_type=self.type,
                    lower_type=lower.__class__))

        if upper is not None and not isinstance(upper, self.type):
            raise TypeError((
                "Invalid type for upper bound '{upper_type.__name__}'"
                " expected '{expected_type.__name__}'").format(
                    expected_type=self.type,
                    upper_type=upper.__class__))

        self._range = _internal_range(
            lower, upper, lower_inc, upper_inc, False)

    @classmethod
    def empty(cls):
        """Returns an empty set."""

        self = cls.__new__(cls)
        self._range = _empty_internal_range
        return self

    def replace(self, *args, **kwargs):
        """
        Returns a new instance of self with the given arguments replaced. It takes
        the exact same arguments as the constructor.

            >>> intrange(1, 5).replace(upper=10)
            intrange([1,10))
            >>> intrange(1, 10).replace(lower_inc=False)
            intrange([2,10))
            >>> intrange(1, 10).replace(5)
            intrange([5,10))

        Note that range objects are immutable and are never modified in place.
        """

        replacements = {
            "lower" : self.lower,
            "upper" : self.upper,
            "lower_inc" : self.lower_inc,
            "upper_inc" : self.upper_inc
        }
        replacements.update(
            dict(zip(("lower", "upper", "lower_inc", "upper_inc"), args)))
        replacements.update(kwargs)

        return self.__class__(**replacements)

    def __repr__(self):
        if not self:
            return "{0.__class__.__name__}(empty)".format(self)
        else:
            return "{instance.__class__.__name__}({lb}{lower},{upper}{ub})".format(
                instance=self,
                lb="[" if self.lower_inc else "(",
                lower="" if self.lower is None else repr(self.lower),
                upper="" if self.upper is None else repr(self.upper),
                ub="]" if self.upper_inc else ")")

    @property
    def lower(self):
        """Returns the lower boundary or None if -infinity"""

        if self:
            return None if self.lower_inf else self._range.lower
        return None

    @property
    def upper(self):
        """Returns the upper boundary or None if infinity"""

        if self:
            return None if self.upper_inf else self._range.upper
        return None

    @property
    def lower_inc(self):
        """
        Returns True if lower bound is included in range. If lower bound is
        -infinity this returns False.
        """

        return False if self.lower_inf else self._range.lower_inc

    @property
    def upper_inc(self):
        """
        Returns True if upper bound is included in range. If upper bound is
        infinity this returns False.
        """

        return False if self.upper_inf else self._range.upper_inc

    @property
    def lower_inf(self):
        """Returns True if lower bound is -infinity."""

        return self._range.lower is None and not self._range.empty

    @property
    def upper_inf(self):
        """Returns True if upper bound is infinity."""

        return self._range.upper is None and not self._range.empty

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._range == other._range

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        elif self.lower == other.lower:
            if self.lower_inc != other.lower_inc:
                return self.lower_inc
            elif self.upper == other.upper:
                return not self.upper_inc and other.upper_inc
            else:
                return self.upper < other.upper
        else:
            return self.lower < other.lower

    def __nonzero__(self):
        return not self._range.empty

    def __contains__(self, item):
        try:
            return self.contains(item)
        except TypeError:
            return NotImplemented

    def __lshift__(self, other):
        return self.left_of(other)

    def __rshift__(self, other):
        return self.right_of(other)

    def contains(self, other):
        """
        Return True if this contains other. Other may be either range of same
        type or scalar of same type as the boundaries.

            >>> intrange(1, 10).contains(intrange(1, 5))
            True
            >>> intrange(1, 10).contains(intrange(5, 10))
            True
            >>> intrange(1, 10).contains(intrange(5, 10, upper_inc=True))
            False
            >>> intrange(1, 10).contains(1)
            True
            >>> intrange(1, 10).contains(10)
            False

        """

        if isinstance(other, self.__class__):
            if not self:
                return bool(other)
            elif not other or other.startsafter(self) and other.endsbefore(self):
                return True
            else:
                return False
        elif isinstance(other, self.type):
            if self.lower_inc and self.upper_inc:
                return self.lower <= other <= self.upper
            elif self.lower_inc:
                return self.lower <= other < self.upper
            elif self.upper_inc:
                return self.lower < other <= self.upper
            else:
                return self.lower < other < self.upper
        else:
            raise TypeError(
                "Unsupported type to test for inclusion '{0.__class__.__name__}'".format(
                    other))

    def within(self, other):
        """Opposite of contains. Tests if this range is within other."""

        if not isinstance(other, self.__class__):
            raise TypeError(
                "Unsupported type to test for inclusion '{0.__class__.__name__}'".format(
                    other))
        return other.contains(self)

    def overlap(self, other):
        """
        Returns True if both ranges share any points.

            >>> intrange(1, 10).overlap(intrange(5, 15))
            True
            >>> intrange(1, 5).overlap(intrange(5, 10))
            False

        """

        return not self << other and not other << self

    def adjacent(self, other):
        """
        Returns True if ranges are directly next to each other but does not
        overlap.

            >>> intrange(1, 5).adjacent(intrange(5, 10))
            True
            >>> intrange(1, 5).adjacent(intrange(10, 15))
            False

        """

        # Must return empty if either is an empty set
        if not self or not other:
            return False
        return (
            (self.lower == other.upper and self.lower_inc != other.upper_inc) or
            (self.upper == other.lower and self.upper_inc != other.lower_inc))

    def union(self, other):
        """
        Unifies two ranges. For this to work the ranges must either overlap or
        be adjacent. If these criterias are not fulfilled ValueError will be
        raised.

            >>> intrange(1, 5).union(intrange(5, 10))
            intrange([1,10))
            >>> intrange(1, 10).union(intrange(5, 15))
            intrange([1,15))
            >>> intrange(1, 5).union(intrange(10, 15))
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            ValueError: Ranges must be either adjacent or overlapping

        """

        # Consider empty ranges
        if not self:
            return other
        elif not other:
            return self
        elif not self.overlap(other) and not self.adjacent(other):
            raise ValueError("Ranges must be either adjacent or overlapping")

        if self.lower == other.lower:
            lower = self.lower
            lower_inc = self.lower_inc or other.lower_inc
        elif self.lower < other.lower:
            lower = self.lower
            lower_inc = self.lower_inc
        else:
            lower = other.lower
            lower_inc = other.lower_inc

        if self.upper == other.upper:
            upper = self.upper
            upper_inc = self.upper_inc or other.upper_inc
        elif self.upper < other.upper:
            upper = other.upper
            upper_inc = other.upper_inc
        else:
            upper = self.upper
            upper_inc = self.upper_inc

        return self.__class__(lower, upper, lower_inc, upper_inc)

    def difference(self, other):
        """
        Returns a new range containing all points in self that are not present
        in other. If all points in other are present in self an empty range is
        returned. A difference call must never split the reference range in two.
        Doing this will raise a ValueError.

            >>> intrange(1, 10).difference(intrange(10, 15))
            intrange([1,10))
            >>> intrange(1, 10).difference(intrange(5, 10))
            intrange([1,5))
            >>> intrange(1, 5).difference(intrange(5, 10))
            intrange([1,5))
            >>> intrange(1, 5).difference(intrange(1, 10))
            intrange(empty)
            >>> intrange(1, 15).difference(intrange(5, 10))
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            ValueError: Other range must not be within this range

        """

        # Consider empty ranges
        if not self or not other:
            return self
        elif self == other or self in other:
            return self.empty()
        elif not self.overlap(other):
            return self
        elif other in self and not (self.startswith(other) or self.endswith(other)):
            raise ValueError("Other range must not be within this range")
        elif self.endsbefore(other):
            return self.replace(upper=other.lower, upper_inc=not other.lower_inc)
        elif self.startsafter(other):
            return self.replace(lower=other.upper, lower_inc=not other.upper_inc)
        else:
            return self.empty()

    def intersection(self, other):
        """
        Returns a new range containing all points shared by both ranges. If no
        points are shared an empty range is returned.

            >>> intrange(1, 5).intersection(intrange(1, 10))
            intrange([1,5))
            >>> intrange(1, 5).intersection(intrange(5, 10))
            intrange(empty)
            >>> intrange(1, 10).intersection(intrange(5, 10))
            intrange([5,10))

        """

        if not self or not other or not self.overlap(other):
            return self.empty()
        elif self.contains(other):
            return other
        elif self.within(other):
            return self

        out = self
        if not self.startsafter(other):
            out = out.replace(lower=other.lower, lower_inc=other.lower_inc)
        if not self.endsbefore(other):
            return out.replace(upper=other.upper, upper_inc=other.upper_inc)
        return out

    def startswith(self, other):
        """
        Returns True if self starts at the same point as other. Other can be
        either range or scalar of the range's type. If range doesn't include the
        start, a scalar other value will always return False.
        """

        if isinstance(other, self.__class__):
            if self.lower_inc == other.lower_inc:
                return self.lower == other.lower
            else:
                return False
        elif isinstance(other, self.type):
            if self.lower_inc:
                return self.lower == other
            else:
                return False
        else:
            raise TypeError(
                "Unsupported type to test for starts with '{0.__class__.__name__}'".format(
                    other))

    def endswith(self, other):
        """
        Returns True if self ends at the same point as other. Other can be
        either range or scalar of the range's type. If range doesn't include the
        end, a scalar other value will always return False.
        """

        if isinstance(other, self.__class__):
            if self.upper_inc == other.upper_inc:
                return self.upper == other.upper
            else:
                return False
        elif isinstance(other, self.type):
            if self.upper_inc:
                return self.upper == other
            else:
                return False
        else:
            raise TypeError(
                "Unsupported type to test for ends with '{0.__class__.__name__}'".format(
                    other))

    def startsafter(self, other):
        """Returns True if self starts either after or the same spot as other."""

        if isinstance(other, self.__class__):
            if self.lower == other.lower:
                return other.lower_inc if self.lower_inc else not other.lower_inc
            elif self.lower_inf:
                return False
            elif other.lower_inf:
                return True
            else:
                return self.lower > other.lower
        elif isinstance(other, self.type):
            return self.lower >= other
        else:
            raise TypeError(
                "Unsupported type to test for starts after '{0.__class__.__name__}'".format(
                    other))

    def endsbefore(self, other):
        """Returns True if self end either before or the same spot as other."""

        if isinstance(other, self.__class__):
            if self.upper == other.upper:
                return other.upper_inc if self.upper_inc else not other.upper_inc
            elif self.upper_inf:
                return False
            elif other.upper_inf:
                return True
            else:
                return self.upper <= other.upper
        elif isinstance(other, self.type):
            return self.upper <= other
        else:
            raise TypeError(
                "Unsupported type to test for ends before '{0.__class__.__name__}'".format(
                    other))

    def left_of(self, other):
        """
        Returns True if self is completely left of other.

            >>> intrange(1, 5).left_of(intrange(5, 10))
            True
            >>> intrange(1, 10).left_of(intrange(5, 10))
            False

        """

        if not self or not other:
            # Handle empty ranges
            return False
        elif self.upper_inf or other.lower_inf:
            return False
        elif self.upper < other.lower:
            return True
        elif self.upper == other.lower:
            return not self.upper_inc or not other.lower_inc
        else:
            return False

    def right_of(self, other):
        """
        Returns True if self is completely right of other.

            >>> intrange(5, 10).right_of(intrange(1, 5))
            True
            >>> intrange(1, 10).right_of(intrange(1, 5))
            False

        """

        return other.left_of(self)

    # Python 3 support
    __bool__ = __nonzero__

class discreterange(range_):
    """
    Discrete ranges are always presented in a normalized form. This means that:

        >>> intrange(0, 5, lower_inc=False)
        intrange([1,5))

    Thus all descrete ranges must provide a unit class attribute containing the
    step length. For intrange this would be:

        class intrange(discreterange):
            type = int
            unit = 1

    A range where no values can fit is considered empty:

        >>> intrange(0, 1, lower_inc=False)
        intrange(empty)

    """

    def __init__(self, *args, **kwargs):
        super(discreterange, self).__init__(*args, **kwargs)

        # Normalize the internal range
        if not self._range.empty:
            lb = self._range.lower
            if not self.lower_inf and not self._range.lower_inc:
                lb = self.next(lb)

            ub = self._range.upper
            if not self.upper_inf and self._range.upper_inc:
                ub = self.next(ub)

            if not self.lower_inf and not self.upper_inf and lb >= ub:
                self._range = _empty_internal_range
            else:
                self._range = _internal_range(lb, ub, True, False, False)

    @classmethod
    def next(cls, curr):
        """Returns the next value for the data type"""

        return curr + cls.step

    def endswith(self, other):
        """
        Discrete ranges are always a closed set and thus we can return True even
        when upper boundary is not included.
        """

        if isinstance(other, self.type):
            if self.upper_inc:
                return self.upper == other
            else:
                return self.upper == self.next(other)
        else:
            return super(discreterange, self).endswith(other)

    def __iter__(self):
        next = self.lower
        while next < self.upper:
            yield next
            next = self.next(next)

class intrange(discreterange):
    """Range that operates on int."""

    __slots__ = ()

    type = int
    step = 1

    def __len__(self):
        return self.upper - self.lower

class floatrange(range_):
    """Range that operates on float."""

    __slots__ = ()

    type = float

class strrange(discreterange):
    # For doctests to work on both python 2 and 3 we need to strip the unicode
    # prefix from the expected output
    __doc__ = u_doctest("""
    Range that operates on unicode strings. Next character is determined
    lexicographically. Representation might seem odd due to normalization.

        >>> strrange(u"a", u"z")
        strrange([{u}'a',{u}'z'))
        >>> strrange(u"a", u"z", upper_inc=True)
        strrange([{u}'a',{u}'{'))

    Iteration over a strrange is only sensible when having single character
    boundaries.

        >>> list(strrange(u"a", u"e", upper_inc=True))
        [{u}'a', {u}'b', {u}'c', {u}'d', {u}'e']
        >>> len(list(strrange(u"aa", u"zz", upper_inc=True))) # doctest: +SKIP
        27852826

    """)

    __slots__ = ()

    type = ustr # Custom cross version unicode type

    @classmethod
    def next(cls, curr):
        # Python's strings are ordered using lexical ordering
        if not curr:
            return ""

        last = curr[-1]

        # Make sure to loop around when we reach the maximum unicode point
        if ord(last) == sys.maxunicode:
            return cls.next(curr[:-1]) + uchr(0)
        else:
            return curr[:-1] + uchr(ord(curr[-1]) + 1)

class daterange(discreterange):
    """Range that operates on datetime's date class."""

    __slots__ = ()

    type = date
    step = timedelta(days=1)

    def __len__(self):
        """
        Returns number of dates in range.

            >>> len(daterange(date(2013, 1, 1), date(2013, 1, 8)))
            7

        """

        if self.lower_inf or self.upper_inf:
            raise ValueError("Unbounded ranges don't have a length")

        return (self.upper - self.lower).days

class datetimerange(range_):
    """Range that operates on datetime's datetime class."""

    __slots__ = ()

    type = datetime

class timedeltarange(range_):
    """Range that operates on datetime's timedelta class."""

    __slots__ = ()

    type = timedelta
