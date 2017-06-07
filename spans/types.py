import operator
import sys

from collections import namedtuple
from datetime import date, datetime, timedelta
from functools import wraps

from ._compat import *
from ._utils import date_from_iso_week, PartialOrderingMixin, PicklableSlotMixin


__all__ = [
    "intrange",
    "floatrange",
    "strrange",
    "daterange",
    "datetimerange",
    "timedeltarange",
    "PeriodRange",
]


_internal_range = namedtuple(
    "_internal_range", ["lower", "upper", "lower_inc", "upper_inc", "empty"])
_empty_internal_range = _internal_range(None, None, False, False, True)


class Range(PartialOrderingMixin, PicklableSlotMixin):
    """
    Abstract base class of all ranges.

    Ranges are very strict about types. This means that both `lower` or `upper`
    must be of the given class or subclass or ``None``.

    All ranges are immutable. No default methods modify the range in place.
    Instead it returns a new instance.

    :param lower: Lower end of range.
    :param upper: Upper end of range.
    :param lower_inc: ``True`` if lower end should be included in range. Default
                      is ``True``
    :param upper_inc: ``True`` if upper end should be included in range. Default
                      is ``False``
    :raises TypeError: If lower or upper bound is not of the correct type.
    :raises ValueError: If upper bound is lower than lower bound.

    .. versionchanged:: 0.5.0
       Changed name from ``range_`` to ``Range``

    .. note::

       All examples in this class uses :class:`~spans.types.intrange` because
       this class is abstract.
    """

    __slots__ = ("_range",)

    def __init__(self, lower=None, upper=None, lower_inc=None, upper_inc=None):
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

        # Verify that lower is less than or equal to upper if both are set to
        # prevent invalid ranges like [10,1)
        if lower is not None and upper is not None and upper < lower:
            raise ValueError(
                "Upper bound ({upper}) is less than lower bound ({lower})".format(
                    upper=upper,
                    lower=lower))

        # Handle default values for lower_inc and upper_inc
        if lower_inc is None:
            lower_inc = True

        if upper_inc is None:
            upper_inc = False

        self._range = _internal_range(
            lower, upper, lower_inc, upper_inc, False)

    @classmethod
    def empty(cls):
        """
        Returns an empty set. An empty set is unbounded and only contain the
        empty set.

            >>> intrange.empty() in intrange.empty()
            True

        It is unbounded but the boundaries are not infinite. Its boundaries are
        returned as ``None``. Every set contains the empty set.
        """

        self = cls.__new__(cls)
        self._range = _empty_internal_range
        return self


    @classmethod
    def is_valid_range(cls, obj):
        return isinstance(obj, cls)

    @classmethod
    def is_valid_scalar(cls, obj):
        return isinstance(obj, cls.type)

    def replace(self, *args, **kwargs):
        """
        replace(lower=None, upper=None, lower_inc=None, upper_inc=None)

        Returns a new instance of self with the given arguments replaced. It
        takes the exact same arguments as the constructor.

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
        """
        Returns the lower boundary or None if it is unbounded.

            >>> intrange(1, 5).lower
            1
            >>> intrange(upper=5).lower

        This is the same as the ``lower(self)`` in PostgreSQL.
        """

        if self:
            return None if self.lower_inf else self._range.lower
        return None

    @property
    def upper(self):
        """
        Returns the upper boundary or None if it is unbounded.

            >>> intrange(1, 5).upper
            5
            >>> intrange(1).upper

        This is the same as the ``upper(self)`` in PostgreSQL.
        """

        if self:
            return None if self.upper_inf else self._range.upper
        return None

    @property
    def lower_inc(self):
        """
        Returns True if lower bound is included in range. If lower bound is
        unbounded this returns False.

            >>> intrange(1, 5).lower_inc
            True

        This is the same as the ``lower_inc(self)`` in PostgreSQL.
        """

        return False if self.lower_inf else self._range.lower_inc

    @property
    def upper_inc(self):
        """
        Returns True if upper bound is included in range. If upper bound is
        unbounded this returns False.

            >>> intrange(1, 5).upper_inc
            False

        This is the same as the ``upper_inc(self)`` in PostgreSQL.
        """

        return False if self.upper_inf else self._range.upper_inc

    @property
    def lower_inf(self):
        """
        Returns True if lower bound is unbounded.

            >>> intrange(1, 5).lower_inf
            False
            >>> intrange(upper=5).lower_inf
            True

        This is the same as the ``lower_inf(self)`` in PostgreSQL.
        """

        return self._range.lower is None and not self._range.empty

    @property
    def upper_inf(self):
        """
        Returns True if upper bound is unbounded.

            >>> intrange(1, 5).upper_inf
            False
            >>> intrange(1).upper_inf
            True

        This is the same as the ``upper_inf(self)`` in PostgreSQL.
        """

        return self._range.upper is None and not self._range.empty

    def __eq__(self, other):
        if not self.is_valid_range(other):
            return NotImplemented
        return self._range == other._range

    def __lt__(self, other):
        if not self.is_valid_range(other):
            return NotImplemented
        # When dealing with empty ranges there is not such thing as order
        elif not self or not other:
            return False
        elif self.lower == other.lower:
            # If lower are equal for both, we need to consider the inclusiveness
            # of both bounds
            if self.lower_inc != other.lower_inc:
                return self.lower_inc
            # If upper bounds are the same, self can only be smaller if it is
            # not inclusive and other is
            elif self.upper == other.upper:
                return not self.upper_inc and other.upper_inc
            elif self.upper_inf or other.upper_inf:
                return other.upper_inf
            else:
                # We need consider the case when an upper bound is infinite
                return self.upper < other.upper
        elif self.lower_inf or other.lower_inf:
            # If self.lower is unbound (infinite) it will always be smaller,
            # unless other.lower is also unbound
            return not other.lower_inf
        else:
            return self.lower < other.lower

    def __gt__(self, other):
        if not self.is_valid_range(other):
            return NotImplemented
        elif not self or not other:
            return False
        return not (self < other or self == other)

    def __nonzero__(self):
        return not self._range.empty

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

        Contains can also be called using the ``in`` operator.

            >>> 1 in intrange(1, 10)
            True

        This is the same as the ``self @> other`` in PostgreSQL.

        :param other: Object to be checked whether it exists within this range
                      or not.
        :return: ``True`` if `other` is completely within this range, otherwise
                 ``False``.
        :raises TypeError: If `other` is not of the correct type.
        """

        if self.is_valid_range(other):
            if not self:
                return not other
            elif not other or other.startsafter(self) and other.endsbefore(self):
                return True
            else:
                return False
        elif self.is_valid_scalar(other):
            # If the lower bounary is not unbound we can safely perform the
            # comparison. Otherwise we'll try to compare a scalar to None, which
            # is bad
            is_within_lower = True
            if not self.lower_inf:
                lower_cmp = operator.le if self.lower_inc else operator.lt
                is_within_lower = lower_cmp(self.lower, other)

            # If the upper bounary is not unbound we can safely perform the
            # comparison. Otherwise we'll try to compare a scalar to None, which
            # is bad
            is_within_upper = True
            if not self.upper_inf:
                upper_cmp = operator.ge if self.upper_inc else operator.gt
                is_within_upper = upper_cmp(self.upper, other)

            return is_within_lower and is_within_upper
        else:
            raise TypeError(
                "Unsupported type to test for inclusion '{0.__class__.__name__}'".format(
                    other))

    def within(self, other):
        """
        Tests if this range is within `other`.

            >>> a = intrange(1, 10)
            >>> b = intrange(3, 8)
            >>> a.contains(b)
            True
            >>> b.within(a)
            True

        This is the same as the ``self <@ other`` in PostgreSQL. One difference
        however is that unlike PostgreSQL ``self`` in this can't be a scalar
        value.

        :param other: Range to test against.
        :return: ``True`` if this range is completely within the given range,
                 otherwise ``False``.
        :raises TypeError: If given range is of the wrong type.

        .. seealso::
           This method is the inverse of :meth:`~spans.types.Range.contains`
        """

        if not self.is_valid_range(other):
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

        This is the same as the ``&&`` operator for two ranges in PostgreSQL.

        :param other: Range to test against.
        :return: ``True`` if ranges overlap, otherwise ``False``.
        :raises TypeError: If `other` is of another type than this range.

        .. seealso::
           If you need to know which part that overlapped, consider using
           :meth:`~spans.types.Range.intersection`.
        """

        # Special case for empty ranges
        if not self or not other:
            return False

        if self < other:
            a, b = self, other
        else:
            a, b = other, self

        # We need to explicitly handle unbounded ranges since a.upper and b.lower
        # make the intervals seem adjacent even though they are not
        if a.upper_inf or b.lower_inf:
            return True
        return a.upper > b.lower or a.upper == b.lower and a.upper_inc and b.lower_inc

    def adjacent(self, other):
        """
        Returns True if ranges are directly next to each other but does not
        overlap.

            >>> intrange(1, 5).adjacent(intrange(5, 10))
            True
            >>> intrange(1, 5).adjacent(intrange(10, 15))
            False

        The empty set is not adjacent to any set.

        This is the same as the ``-|-`` operator for two ranges in PostgreSQL.

        :param other: Range to test against.
        :return: ``True`` if this range is adjacent with `other`, otherwise
                 ``False``.
        :raises TypeError: If given argument is of invalid type
        """

        if not self.is_valid_range(other):
            raise TypeError(
                "Unsupported type to test for inclusion '{0.__class__.__name__}'".format(
                    other))
        # Must return False if either is an empty set
        elif not self or not other:
            return False
        return (
            (self.lower == other.upper and self.lower_inc != other.upper_inc) or
            (self.upper == other.lower and self.upper_inc != other.lower_inc))

    def union(self, other):
        """
        Merges this range with a given range.

            >>> intrange(1, 5).union(intrange(5, 10))
            intrange([1,10))
            >>> intrange(1, 10).union(intrange(5, 15))
            intrange([1,15))

        Two ranges can not be merged if the resulting range would be split in
        two. This happens when the two sets are neither adjacent nor overlaps.

            >>> intrange(1, 5).union(intrange(10, 15))
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            ValueError: Ranges must be either adjacent or overlapping

        This does not modify the range in place.

        This is the same as the ``+`` operator for two ranges in PostgreSQL.

        :param other: Range to merge with.
        :return: A new range that is the union of this and `other`.
        :raises ValueError: If `other` can not be merged with this range.
        """

        if not self.is_valid_range(other):
            msg = "Unsupported type to test for union '{.__class__.__name__}'"
            raise TypeError(msg.format(other))

        # Optimize empty ranges
        if not self:
            return other
        elif not other:
            return self

        # Order ranges to simplify checks
        if self < other:
            a, b = self, other
        else:
            a, b = other, self

        if a.upper <= b.lower and not a.adjacent(b):
            raise ValueError("Ranges must be either adjacent or overlapping")

        # a.lower is guaranteed to be the lower bound, but either a.upper or
        # b.upper can be the upper bound
        if a.upper == b.upper:
            upper = a.upper
            upper_inc = a.upper_inc or b.upper_inc
        elif a.upper < b.upper:
            upper = b.upper
            upper_inc = b.upper_inc
        else:
            upper = a.upper
            upper_inc = a.upper_inc

        return self.__class__(a.lower, upper, a.lower_inc, upper_inc)

    def difference(self, other):
        """
        Compute the difference between this and a given range.

            >>> intrange(1, 10).difference(intrange(10, 15))
            intrange([1,10))
            >>> intrange(1, 10).difference(intrange(5, 10))
            intrange([1,5))
            >>> intrange(1, 5).difference(intrange(5, 10))
            intrange([1,5))
            >>> intrange(1, 5).difference(intrange(1, 10))
            intrange(empty)

        The difference can not be computed if the resulting range would be split
        in two separate ranges. This happens when the given range is completely
        within this range and does not start or end at the same value.

            >>> intrange(1, 15).difference(intrange(5, 10))
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            ValueError: Other range must not be within this range

        This does not modify the range in place.

        This is the same as the ``-`` operator for two ranges in PostgreSQL.

        :param other: Range to difference against.
        :return: A new range that is the difference between this and `other`.
        :raises ValueError: If difference bethween this and `other` can not be
                            computed.
        """

        if not self.is_valid_range(other):
            msg = "Unsupported type to test for difference '{.__class__.__name__}'"
            raise TypeError(msg.format(other))

        # Consider empty ranges or no overlap
        if not self or not other or not self.overlap(other):
            return self
        # If self is contained within other, the result is empty
        elif self in other:
            return self.empty()
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

        This is the same as the ``+`` operator for two ranges in PostgreSQL.

        :param other: Range to interect with.
        :return: A new range that is the intersection between this and `other`.
        """

        if not self.is_valid_range(other):
            msg = "Unsupported type to test for intersection '{.__class__.__name__}'"
            raise TypeError(msg.format(other))

        # Handle ranges not intersecting
        if not self or not other or not self.overlap(other):
            return self.empty()

        lower_end_span = self if self.startsafter(other) else other
        upper_end_span = self if self.endsbefore(other) else other

        return lower_end_span.replace(
            upper=upper_end_span.upper,
            upper_inc=upper_end_span.upper_inc)

    def startswith(self, other):
        """
        Test if this range starts with `other`. `other` may be either range or
        scalar.

            >>> intrange(1, 5).startswith(1)
            True
            >>> intrange(1, 5).startswith(intrange(1, 10))
            True

        :param other: Range or scalar to test.
        :return: ``True`` if this range starts with `other`, otherwise ``False``
        :raises TypeError: If `other` is of the wrong type.
        """

        if self.is_valid_range(other):
            if self.lower_inc == other.lower_inc:
                return self.lower == other.lower
            else:
                return False
        elif self.is_valid_scalar(other):
            if self.lower_inc:
                return self.lower == other
            else:
                return False
        else:
            raise TypeError(
                "Unsupported type to test for starts with '{}'".format(
                    other.__class__.__name__))

    def endswith(self, other):
        """
        Test if this range ends with `other`. `other` may be either range or
        scalar.

            >>> intrange(1, 5).endswith(4)
            True
            >>> intrange(1, 10).endswith(intrange(5, 10))
            True

        :param other: Range or scalar to test.
        :return: ``True`` if this range ends with `other`, otherwise ``False``
        :raises TypeError: If `other` is of the wrong type.
        """

        if self.is_valid_range(other):
            if self.upper_inc == other.upper_inc:
                return self.upper == other.upper
            else:
                return False
        elif self.is_valid_scalar(other):
            if self.upper_inc:
                return self.upper == other
            else:
                return False
        else:
            raise TypeError(
                "Unsupported type to test for ends with '{}'".format(
                    other.__class__.__name__))

    def startsafter(self, other):
        """
        Test if this range starts after `other`. `other` may be either range or
        scalar. This only takes the lower end of the ranges into consideration.
        If the scalar or the lower end of the given range is greater than or
        equal to this range's lower end, ``True`` is returned.

            >>> intrange(1, 5).startsafter(0)
            True
            >>> intrange(1, 5).startsafter(intrange(0, 5))
            True

        If ``other`` has the same start as the given

        :param other: Range or scalar to test.
        :return: ``True`` if this range starts after `other`, otherwise ``False``
        :raises TypeError: If `other` is of the wrong type.
        """

        if self.is_valid_range(other):
            if self.lower == other.lower:
                return other.lower_inc or not self.lower_inc
            elif self.lower_inf:
                return False
            elif other.lower_inf:
                return True
            else:
                return self.lower > other.lower
        elif self.is_valid_scalar(other):
            return self.lower >= other
        else:
            raise TypeError(
                "Unsupported type to test for starts after '{}'".format(
                    other.__class__.__name__))

    def endsbefore(self, other):
        """
        Test if this range ends before `other`. `other` may be either range or
        scalar. This only takes the upper end of the ranges into consideration.
        If the scalar or the upper end of the given range is less than or equal
        to this range's upper end, ``True`` is returned.

            >>> intrange(1, 5).endsbefore(5)
            True
            >>> intrange(1, 5).endsbefore(intrange(1, 5))
            True

        :param other: Range or scalar to test.
        :return: ``True`` if this range ends before `other`, otherwise ``False``
        :raises TypeError: If `other` is of the wrong type.
        """

        if self.is_valid_range(other):
            if self.upper == other.upper:
                return not self.upper_inc or other.upper_inc
            elif self.upper_inf:
                return False
            elif other.upper_inf:
                return True
            else:
                return self.upper <= other.upper
        elif self.is_valid_scalar(other):
            return self.upper <= other
        else:
            raise TypeError(
                "Unsupported type to test for ends before '{}'".format(
                    other.__class__.__name__))

    def left_of(self, other):
        """
        Test if this range `other` is strictly left of `other`.

            >>> intrange(1, 5).left_of(intrange(5, 10))
            True
            >>> intrange(1, 10).left_of(intrange(5, 10))
            False

        The bitwise right shift operator ``<<`` is overloaded for this operation
        too.

            >>> intrange(1, 5) << intrange(5, 10)
            True

        The choice of overloading ``<<`` might seem strange, but it is to mimick
        PostgreSQL's operators for ranges. As this is not obvious the use of
        ``<<`` is discouraged.

        :param other: Range to test against.
        :return: ``True`` if this range is completely to the left of ``other``.
        """

        if not self.is_valid_range(other):
            msg = (
                "Left of is not supported for '{}', provide a proper range "
                "class").format(other.__class__.__name__)
            raise TypeError(msg)

        return self < other and not self.overlap(other)

    def right_of(self, other):
        """
        Test if this range `other` is strictly right of `other`.

            >>> intrange(5, 10).right_of(intrange(1, 5))
            True
            >>> intrange(1, 10).right_of(intrange(1, 5))
            False

        The bitwise right shift operator ``>>`` is overloaded for this operation
        too.

            >>> intrange(5, 10) >> intrange(1, 5)
            True

        The choice of overloading ``>>`` might seem strange, but it is to mimick
        PostgreSQL's operators for ranges. As this is not obvious the use of
        ``>>`` is discouraged.

        :param other: Range to test against.
        :return: ``True`` if this range is completely to the right of ``other``.
        """

        if not self.is_valid_range(other):
            msg = (
                "Right of is not supported for '{}', provide a proper range "
                "class").format(other.__class__.__name__)
            raise TypeError(msg)

        return other.left_of(self)

    def __lshift__(self, other):
        try:
            return self.left_of(other)
        except TypeError:
            return NotImplemented

    def __rshift__(self, other):
        try:
            return self.right_of(other)
        except TypeError:
            return NotImplemented

    def __or__(self, other):
        try:
            return self.union(other)
        except TypeError:
            return NotImplemented

    def __and__(self, other):
        try:
            return self.intersection(other)
        except TypeError:
            return NotImplemented

    def __sub__(self, other):
        try:
            return self.difference(other)
        except TypeError:
            return NotImplemented

    # ``in`` operator support
    __contains__ = contains

    # Python 3 support
    __bool__ = __nonzero__


class DiscreteRange(Range):
    """
    DiscreteRange(lower=None, upper=None, lower_inc=None, upper_inc=None)

    Discrete ranges are a subset of ranges that works on discrete types. This
    includes ``int`` and ``datetime.date``.

        >>> intrange(0, 5, lower_inc=False)
        intrange([1,5))
        >>> intrange(0, 5, lower_inc=False).lower_inc
        True

    All discrete ranges must provide a unit attribute containing the step
    length. For intrange this would be:

    .. code-block:: python

        class intrange(DiscreteRange):
            type = int
            unit = 1

    A range where no values can fit is considered empty:

        >>> intrange(0, 1, lower_inc=False)
        intrange(empty)

    Discrete ranges are iterable.

        >>> list(intrange(1, 5))
        [1, 2, 3, 4]

    .. versionchanged:: 0.5.0
       Changed name from ``discreterange`` to ``DiscreteRange``
    """

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(DiscreteRange, self).__init__(*args, **kwargs)

        # Normalize the internal range
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
        """
        Increment the given value with the step defined for this class.

            >>> intrange.next(1)
            2

        :param curr: Value to increment.
        :return: Incremented value.
        """

        return curr + cls.step

    @classmethod
    def prev(cls, curr):
        """
        Decrement the given value with the step defined for this class.

            >>> intrange.prev(1)
            0

        :param curr: Value to decrement.
        :return: Decremented value.
        """

        return curr - cls.step

    @property
    def last(self):
        """
        Returns the last element within this range. If the range has no upper
        limit ``None`` is returned.

            >>> intrange(1, 10).last
            9
            >>> intrange(1, 10, upper_inc=True).last
            10
            >>> intrange(1).last is None
            True

        :return: Last element within this range.

        .. versionadded:: 0.1.4
        """

        if not self or self.upper_inf:
            return None
        else:
            # This is always valid since discrete sets are normalized to upper
            # bound not included
            return self.prev(self.upper)

    def endswith(self, other):
        # Discrete ranges have a last element even in cases when upper bound is
        # not included in set
        if self.is_valid_scalar(other):
            return self.last == other
        else:
            return super(DiscreteRange, self).endswith(other)

    def __iter__(self):
        if self.lower_inf:
            raise TypeError("Range with no lower bound can't be iterated over")

        value = self.lower
        while self.upper_inf or value < self.upper:
            yield value
            value = self.next(value)

    def __reversed__(self):
        if self.upper_inf:
            raise TypeError("Range with no upper bound can't be iterated over")

        value = self.last
        while self.lower_inf or value >= self.lower:
            yield value
            value = self.prev(value)


class OffsetableRangeMixin(object):
    """
    Mixin for range types that supports being offset by a value. This value must
    be of the same type as the range boundaries. For date types this will not
    work and can be solved by explicitly defining an ``offset_type``:

    .. code-block:: python

        class datetimerange(Range, OffsetableRangeMixin):
            __slots__ = ()

            type = datetime
            offset_type = timedelta

    .. versionchanged:: 0.5.0
       Changed name from ``offsetablerange`` to ``OffsetableRangeMixin``
    """

    __slots__ = ()

    offset_type = None

    def offset(self, offset):
        """
        Shift the range to the left or right with the given offset

            >>> intrange(0, 5).offset(5)
            intrange([5,10))
            >>> intrange(5, 10).offset(-5)
            intrange([0,5))
            >>> intrange.empty().offset(5)
            intrange(empty)

        Note that range objects are immutable and are never modified in place.

        :param offset: Scalar to offset by.

        .. versionadded:: 0.1.3
        """

        # If range is empty it can't be offset
        if not self:
            return self

        offset_type = self.type if self.offset_type is None else self.offset_type

        if offset is not None and not isinstance(offset, offset_type):
            raise TypeError((
                "Invalid type for offset '{offset_type.__name__}'"
                " expected '{expected_type.__name__}'").format(
                    expected_type=offset_type,
                    offset_type=offset.__class__))

        lower = None if self.lower is None else self.lower + offset
        upper = None if self.upper is None else self.upper + offset

        return self.replace(lower=lower, upper=upper)


class intrange(DiscreteRange, OffsetableRangeMixin):
    """
    Range that operates on int.

        >>> intrange(1, 5)
        intrange([1,5))

    Inherits methods from :class:`~spans.types.Range`,
    :class:`~spans.types.DiscreteRange` and :class:`~spans.types.OffsetableRangeMixin`.
    """

    __slots__ = ()

    type = int
    step = 1

    def __len__(self):
        return self.upper - self.lower


class floatrange(Range, OffsetableRangeMixin):
    """
    Range that operates on float.

        >>> floatrange(1.0, 5.0)
        floatrange([1.0,5.0))

    Inherits methods from :class:`~spans.types.Range` and
    :class:`~spans.types.OffsetableRangeMixin`.
    """

    __slots__ = ()

    type = float


class strrange(DiscreteRange):
    """
    Range that operates on unicode strings. Next character is determined
    lexicographically. Representation might seem odd due to normalization.

        >>> strrange(u"a", u"z")
        strrange([u'a',u'z'))
        >>> strrange(u"a", u"z", upper_inc=True)
        strrange([u'a',u'{'))

    Iteration over a strrange is only sensible when having single character
    boundaries.

        >>> list(strrange(u"a", u"e", upper_inc=True))
        [u'a', u'b', u'c', u'd', u'e']
        >>> len(list(strrange(u"aa", u"zz", upper_inc=True))) # doctest: +SKIP
        27852826

    Inherits methods from :class:`~spans.types.Range` and
    :class:`~spans.types.DiscreteRange`.
    """

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

    @classmethod
    def prev(cls, curr):
        # Python's strings are ordered using lexical ordering
        if not curr:
            return ""

        last = curr[-1]

        # Make sure to loop around when we reach the minimum unicode point
        if ord(last) == 0:
            return cls.prev(curr[:-1]) + uchr(sys.maxunicode)
        else:
            return curr[:-1] + uchr(ord(curr[-1]) - 1)


def _is_valid_date(obj, accept_none=True):
    """
    Check if an object is an instance of, or a subclass deriving from, a
    ``date``. However, it does not consider ``datetime`` or subclasses thereof
    as valid dates.

    :param obj: Object to test as date.
    :param accept_none: If True None is considered as a valid date object.
    """

    if accept_none and obj is None:
        return True
    return isinstance(obj, date) and not isinstance(obj, datetime)


class daterange(DiscreteRange, OffsetableRangeMixin):
    """
    Range that operates on ``datetime.date``.

        >>> daterange(date(2015, 1, 1), date(2015, 2, 1))
        daterange([datetime.date(2015, 1, 1),datetime.date(2015, 2, 1)))

    Offsets are done using ``datetime.timedelta``.

        >>> daterange(date(2015, 1, 1), date(2015, 2, 1)).offset(timedelta(14))
        daterange([datetime.date(2015, 1, 15),datetime.date(2015, 2, 15)))

    Inherits methods from :class:`~spans.types.Range`,
    :class:`~spans.types.DiscreteRange` and :class:`~spans.types.OffsetableRangeMixin`.
    """

    __slots__ = ()

    type = date
    offset_type = timedelta
    step = timedelta(days=1)

    def __init__(self, lower=None, upper=None, lower_inc=None, upper_inc=None):
        if not _is_valid_date(lower, accept_none=True):
            raise TypeError((
                "Invalid type for lower bound '{lower_type.__name__}'"
                " expected '{expected_type.__name__}'").format(
                    expected_type=self.type,
                    lower_type=lower.__class__))

        if not _is_valid_date(upper, accept_none=True):
            raise TypeError((
                "Invalid type for upper bound '{upper_type.__name__}'"
                " expected '{expected_type.__name__}'").format(
                    expected_type=self.type,
                    upper_type=upper.__class__))

        super(daterange, self).__init__(lower, upper, lower_inc, upper_inc)

    @classmethod
    def from_date(cls, date, period=None):
        """
        Create a day long daterange from for the given date.

            >>> daterange.from_date(date(2000, 1, 1))
            daterange([datetime.date(2000, 1, 1),datetime.date(2000, 1, 2)))

        :param date: A date to convert.
        :param period: The period to normalize date to. A period may be one of:
                       ``day`` (default), ``week``, ``american_week``,
                       ``month``, ``quarter`` or ``year``.
        :return: A new range that contains the given date.


        .. seealso::

           There are convenience methods for most period types:
           :meth:`~spans.types.daterange.from_week`,
           :meth:`~spans.types.daterange.from_month`,
           :meth:`~spans.types.daterange.from_quarter` and
           :meth:`~spans.types.daterange.from_year`.

           :class:`~spans.types.PeriodRange` has the same interface but is
           period aware. This means it is possible to get things like next week
           or month.

        .. versionchanged:: 0.4.0
           Added the period parameter.
        """

        if period is None or period == "day":
            return cls(date, date, upper_inc=True)
        elif period == "week":
            start = date - timedelta(date.weekday())
            return cls(start, start + timedelta(7))
        elif period == "american_week":
            start = date - timedelta((date.weekday() + 1) % 7)
            return cls(start, start + timedelta(7))
        elif period == "month":
            start = date.replace(day=1)
            return cls(start, (start + timedelta(31)).replace(day=1))
        elif period == "quarter":
            start = date.replace(month=(date.month - 1) // 3 * 3 + 1, day=1)
            return cls(start, (start + timedelta(93)).replace(day=1))
        elif period == "year":
            start = date.replace(month=1, day=1)
            return cls(start, (start + timedelta(366)).replace(day=1))
        else:
            raise ValueError("Unexpected period, got {!r}".format(period))

    @classmethod
    def from_week(cls, year, iso_week):
        """
        Create ``daterange`` based on a year and an ISO week

        :param year: Year as an integer
        :param iso_week: ISO week number
        :return: A new ``daterange`` for the given week

        .. versionadded:: 0.4.0
        """

        first_day = date_from_iso_week(year, iso_week)
        return cls.from_date(first_day, period="week")

    # NOTE: from_american_week doesn't exist since I don't know enough about
    #       their calendar, if they even use enumerated weeks.

    @classmethod
    def from_month(cls, year, month):
        """
        Create ``daterange`` based on a year and amonth

        :param year: Year as an integer
        :param iso_week: Month as an integer between 1 and 12
        :return: A new ``daterange`` for the given month

        .. versionadded:: 0.4.0
        """

        first_day = date(year, month, 1)
        return cls.from_date(first_day, period="month")

    @classmethod
    def from_quarter(cls, year, quarter):
        """
        Create ``daterange`` based on a year and quarter.

        A quarter is considered to be:

        - January through March (Q1),
        - April through June (Q2),
        - July through September (Q3) or,
        - October through December (Q4)

        :param year: Year as an integer
        :param quarter: Quarter as an integer between 1 and 4
        :return: A new ``daterange`` for the given quarter

        .. versionadded:: 0.4.0
        """

        quarter_months = {
            1: 1,
            2: 4,
            3: 7,
            4: 10,
        }

        if quarter not in quarter_months:
            error_msg = (
                "quarter is not a valid quarter. Expected a value between 1 "
                "and 4 got {!r}")
            raise ValueError(error_msg.format(quarter))

        first_day = date(year, quarter_months[quarter], 1)
        return cls.from_date(first_day, period="quarter")

    @classmethod
    def from_year(cls, year):
        """
        Create ``daterange`` based on a year

        :param year: Year as an integer
        :return: A new ``daterange`` for the given year

        .. versionadded:: 0.4.0
        """

        first_day = date(year, 1, 1)
        return cls.from_date(first_day, period="year")

    def __len__(self):
        """
        Returns number of dates in range.

            >>> len(daterange(date(2013, 1, 1), date(2013, 1, 8)))
            7

        """

        if self.lower_inf or self.upper_inf:
            raise ValueError("Unbounded ranges don't have a length")

        return (self.upper - self.lower).days


class datetimerange(Range, OffsetableRangeMixin):
    """
    Range that operates on ``datetime.datetime``.

        >>> datetimerange(datetime(2015, 1, 1), datetime(2015, 2, 1))
        datetimerange([datetime.datetime(2015, 1, 1, 0, 0),datetime.datetime(2015, 2, 1, 0, 0)))

    Offsets are done using ``datetime.timedelta``.

        >>> datetimerange(
        ...     datetime(2015, 1, 1), datetime(2015, 2, 1)).offset(timedelta(14))
        datetimerange([datetime.datetime(2015, 1, 15, 0, 0),datetime.datetime(2015, 2, 15, 0, 0)))

    Inherits methods from :class:`~spans.types.Range` and :class:`~spans.types.OffsetableRangeMixin`.
    """

    __slots__ = ()

    type = datetime
    offset_type = timedelta


class timedeltarange(Range, OffsetableRangeMixin):
    """
    Range that operates on datetime's timedelta class.

        >>> timedeltarange(timedelta(1), timedelta(5))
        timedeltarange([datetime.timedelta(1),datetime.timedelta(5)))

    Offsets are done using ``datetime.timedelta``.

        >>> timedeltarange(timedelta(1), timedelta(5)).offset(timedelta(14))
        timedeltarange([datetime.timedelta(15),datetime.timedelta(19)))

    Inherits methods from :class:`~spans.types.Range` and
    :class:`~spans.types.OffsetableRangeMixin`.
    """

    __slots__ = ()

    type = timedelta


class PeriodRange(daterange):
    """
    A type aware version of :class:`~spans.types.daterange`.

    Type aware refers to being aware of what kind of range it represents.
    Available types are the same as the ``period`` argument for to
    :meth:`~spans.types.daterange.from_date`.

    Some methods are unavailable due since they don't make sense for
    :class:`~spans.types.PeriodRange`, and some may return a normal
    :class:`~spans.types.daterange` since they may modifify the range in ways
    not compatible with its type.

    .. versionadded:: 0.4.0

    .. note::

       This class does not have its own range set implementation, but can be
       used with :class:`~spans.settypes.daterangeset`.
    """

    __slots__ = ("period")

    @classmethod
    def empty(cls):
        """
        :raise TypeError: since typed date ranges must never be empty
        """

        raise TypeError("{} does not support empty ranges".format(cls.__name__))

    # We override the is valid check here because dateranges will not be
    # accepted as valid arguments otherwise.
    @classmethod
    def is_valid_range(cls, other):
        return isinstance(other, daterange)

    @classmethod
    def from_date(cls, day, period=None):
        span = daterange.from_date(day, period=period)

        new_span = cls()
        new_span._range = span._range
        new_span.period = period

        return new_span

    @property
    def daterange(self):
        """
        This ``PeriodRange`` represented as a naive
        :class:`~spans.types.daterange`.
        """

        return daterange(
            lower=self.lower,
            upper=self.upper,
            lower_inc=self.lower_inc,
            upper_inc=self.upper_inc)

    def offset(self, offset):
        """
        Offset the date range by the given amount of periods.

        This differs from :meth:`~spans.types.OffsetableRangeMixin.offset` on
        :class:`spans.types.daterange` by not accepting a ``timedelta`` object.
        Instead it expects an integer to adjust the typed date range by. The
        given value may be negative as well.

        :param offset: Number of periods to offset this range by. A period is
                       either a day, week, american week, month, quarter or
                       year, depending on this range's period type.
        :return: New offset :class:`~spans.types.PeriodRange`
        """

        span = self
        if offset > 0:
            for i in iter_range(offset):
                span = span.next_period()
        elif offset < 0:
            for i in iter_range(-offset):
                span = span.prev_period()
        return span

    def prev_period(self):
        """
        The period before this range.

            >>> span = PeriodRange.from_date(date(2000, 1, 1), period="month")
            >>> span.prev_period()
            PeriodRange([datetime.date(1999, 12, 1),datetime.date(2000, 1, 1)))

        :return: A new :class:`~spans.types.PeriodRange` for the period
                 before this period
        """

        return self.from_date(self.prev(self.lower), period=self.period)

    def next_period(self):
        """
        The period after this range.

            >>> span = PeriodRange.from_date(date(2000, 1, 1), period="month")
            >>> span.next_period()
            PeriodRange([datetime.date(2000, 2, 1),datetime.date(2000, 3, 1)))

        :return: A new :class:`~spans.types.PeriodRange` for the period after
                 this period
        """

        # We can use this shortcut since dateranges are always normalized
        return self.from_date(self.upper, period=self.period)

    # Override methods that modifies the range to return a daterange instead
    def replace(self, *args, **kwargs):
        return self.daterange.replace(*args, **kwargs)

    def union(self, other):
        return self.daterange.union(other)

    def intersection(self, other):
        return self.daterange.intersection(other)

    def difference(self, other):
        return self.daterange.difference(other)


# Legacy names

#: This alias exist for legacy reasons. It is considered deprecated but will not
#: likely be removed.
#:
#: .. versionadded:: 0.5.0
range_ = Range


#: This alias exist for legacy reasons. It is considered deprecated but will not
#: likely be removed.
#:
#: .. versionadded:: 0.5.0
discreterange = DiscreteRange


#: This alias exist for legacy reasons. It is considered deprecated but will not
#: likely be removed.
#:
#: .. versionadded:: 0.5.0
offsetablerange = OffsetableRangeMixin
