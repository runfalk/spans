from itertools import chain

from ._compat import add_metaclass
from ._utils import sane_total_ordering
from .types import range_
from .types import *
from .types import discreterange, offsetablerange

# Imports needed for doctests in date range sets
from datetime import *


__all__ = [
    "intrangeset",
    "floatrangeset",
    "strrangeset",
    "daterangeset",
    "datetimerangeset",
    "timedeltarangeset",
]


class metarangeset(type):
    """
    A meta class for rangesets. The purpose is to automatically add relevant
    mixins to the range set class based on what mixins and baseclasses the range
    class has.
    """

    mixin_map = {}

    def __new__(cls, name, bases, attrs):
        parents = list(bases)

        if "type" in attrs:
            for rangemixin, rangesetmixin in cls.mixin_map.items():
                if issubclass(attrs["type"], rangemixin):
                    parents.append(rangesetmixin)

        return super(metarangeset, cls).__new__(cls, name, tuple(parents), attrs)

    @classmethod
    def add(cls, range_mixin, range_set_mixin):
        cls.mixin_map[range_mixin] = range_set_mixin

    @classmethod
    def register(cls, range_mixin):
        def decorator(range_set_mixin):
            cls.add(range_mixin, range_set_mixin)
            return range_set_mixin
        return decorator


@metarangeset.register(discreterange)
class discreterangeset(object):
    """
    Mixin that adds support for discrete range set operations. Automatically used
    by rangeset when range type inherits discreterange

    See also :class:`~spans.types.discreterange`.
    """

    __slots__ = ()

    def values(self):
        """
        Returns an iterator over each value in this range set.

            >>> list(intrangeset([intrange(1, 5), intrange(10, 15)]).values())
            [1, 2, 3, 4, 10, 11, 12, 13, 14]

        """

        return chain(*self)


@metarangeset.register(offsetablerange)
class offsetablerangeset(object):
    """
    Mixin that adds support for offsetable range set operations. Automatically used
    by rangeset when range type inherits offsetablerange.

    See also :meth:`spans.types.offsetablerange`.
    """

    __slots__ = ()

    def offset(self, offset):
        """
        Shift the range set to the left or right with the given offset

            >>> intrangeset([intrange(0, 5), intrange(10, 15)]).offset(5)
            intrangeset([intrange([5,10)), intrange([15,20))])
            >>> intrangeset([intrange(5, 10), intrange(15, 20)]).offset(-5)
            intrangeset([intrange([0,5)), intrange([10,15))])

        This function returns an offset copy of the original set, i.e. updating
        is not done in place.
        """

        return self.__class__(r.offset(offset) for r in self)


@sane_total_ordering
@add_metaclass(metarangeset)
class rangeset(object):
    """
    A range set works a lot like a range with some differences:

    - All range sets supports ``len()``. Cardinality for a range set means the
      number of distinct ranges required to represent this set. See
      :meth:`~spans.settypes.rangeset.__len__`.
    - All range sets are iterable. The iterator returns a range for each
      iteration. See :meth:`~spans.settypes.rangeset.__iter__` for more details.
    - All range sets are invertible using the ``~`` operator. The result is a
      new range set that does not intersect the original range set at all.

          >>> ~intrangeset([intrange(1, 5)])
          intrangeset([intrange((,1)), intrange([5,))])

    - Contrary to ranges. A range set may be split into multiple ranges when
      performing set operations such as union, difference or intersection.

    .. tip::
        The ``rangeset`` constructor supports any iterable sequence as argument.

    :param ranges: A sequence of ranges to add to this set.
    :raises TypeError: If any of the given ranges are of incorrect type.
    """

    __slots__ = ("_list",)

    def __init__(self, ranges):
        self._list = []

        for r in ranges:
            self.add(r)

    def __repr__(self):
        return "{instance.__class__.__name__}({list!r})".format(
            instance=self,
            list=self._list)

    # Support pickling using the default ancient pickling protocol for Python 2.7
    def __getstate__(self):
        return self._list

    def __setstate__(self, state):
        self._list = state

    def __nonzero__(self):
        """
        Returns False if the only thing in this set is the empty set, otherwise
        it returns True.

            >>> bool(intrangeset([]))
            False
            >>> bool(intrangeset([intrange(1, 5)]))
            True

        """
        return bool(self._list)

    def __iter__(self):
        """
        Returns an iterator over all ranges within this set. Note that this
        iterates over the normalized version of the range set:

            >>> list(intrangeset(
            ...     [intrange(1, 5), intrange(5, 10), intrange(15, 20)]))
            [intrange([1,10)), intrange([15,20))]

        If the set is empty an empty iterator is returned.

            >>> list(intrangeset([]))
            []

        .. versionchanged:: 0.3.0
           This method used to return an empty range when the rangeset was
           empty.
        """

        return iter(self._list)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._list == other._list

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._list < other._list

    def __len__(self):
        """
        Returns the cardinality of the set which is 0 for the empty set or else
        the number of ranges used to represent this range set.

            >>> len(intrangeset([]))
            0
            >>> len(intrangeset([intrange(1,5)]))
            1
            >>> len(intrangeset([intrange(1,5),intrange(10,20)]))
            2


        .. versionadded:: 0.2.0
        """
        return len(self._list)

    def __invert__(self):
        """
        Returns an inverted version of this set. The inverted set contains no
        values this contains.

            >>> ~intrangeset([intrange(1, 5)])
            intrangeset([intrange((,1)), intrange([5,))])

        """

        return self.__class__([self.type()]).difference(self)

    def _test_type(self, item):
        if not isinstance(item, self.type):
            raise TypeError((
                "Invalid range type '{range_type.__name__}' expected "
                "'{expected_type.__name__}'").format(
                    expected_type=self.type,
                    range_type=item.__class__))

    def copy(self):
        """
        Makes a copy of this set. This copy is not deep since ranges are
        immutable.

            >>> rs = intrangeset([intrange(1, 5)])
            >>> rs_copy = rs.copy()
            >>> rs == rs_copy
            True
            >>> rs is rs_copy
            False

        :return: A new range set with the same ranges as this range set.
        """

        return self.__class__(self)

    def contains(self, item):
        """
        Test if this range
        Return True if one range within the set contains elem, which may be
        either a range of the same type or a scalar of the same type as the
        ranges within the set.

            >>> intrangeset([intrange(1, 5)]).contains(3)
            True
            >>> intrangeset([intrange(1, 5), intrange(10, 20)]).contains(7)
            False
            >>> intrangeset([intrange(1, 5)]).contains(intrange(2, 3))
            True
            >>> intrangeset(
            ...     [intrange(1, 5), intrange(8, 9)]).contains(intrange(4, 6))
            False

        Contains can also be called using the ``in`` operator.

            >>> 3 in intrangeset([intrange(1, 5)])
            True

        This operation is `O(n)` where `n` is the number of ranges within this
        range set.

        :param item: Range or scalar to test for.
        :return: True if element is contained within this set.

        .. versionadded:: 0.2.0
        """

        # All range sets contain the empty range. However, we must verify the
        # type of what is being passed as well to make sure we indeed got an
        # empty set of the correct type.
        if isinstance(item, self.type) and not item:
            return True

        for r in self._list:
            if r.contains(item) is True:
                return True
        return False

    def add(self, item):
        """
        Adds a range to the set.

            >>> rs = intrangeset([])
            >>> rs.add(intrange(1, 10))
            >>> rs
            intrangeset([intrange([1,10))])
            >>> rs.add(intrange(5, 15))
            >>> rs
            intrangeset([intrange([1,15))])
            >>> rs.add(intrange(20, 30))
            >>> rs
            intrangeset([intrange([1,15)), intrange([20,30))])

        This operation updates the set in place.

        :param item: Range to add to this set.
        :raises TypeError: If any of the given ranges are of incorrect type.
        """

        self._test_type(item)

        # If item is empty, do not add it
        if not item:
            return

        i = 0
        buffer = []
        while i < len(self._list):
            r = self._list[i]

            #import pdb; pdb.set_trace()
            if r.overlap(item) or r.adjacent(item):
                buffer.append(self._list.pop(i))
                continue
            elif item.left_of(r):
                # If there are buffered items we must break here for the buffer
                # to be inserted
                if not buffer:
                    self._list.insert(i, item)
                break
            i += 1
        else:
            # The list was exausted and the range should be appended unless there
            # are ranges in the buffer
            if not buffer:
                self._list.append(item)

        # Process the buffer
        if buffer:
            # Unify the buffer
            for r in buffer:
                item = item.union(r)
            self.add(item)

    def remove(self, item):
        """
        Remove a range from the set. This operation updates the set in place.

            >>> rs = intrangeset([intrange(1, 15)])
            >>> rs.remove(intrange(5, 10))
            >>> rs
            intrangeset([intrange([1,5)), intrange([10,15))])

        :param item: Range to remove from this set.
        """

        self._test_type(item)

        # If the list currently only have an empty range do nothing since an
        # empty rangeset can't be removed from anyway.
        if not self:
            return

        i = 0
        while i < len(self._list):
            r = self._list[i]
            if item.left_of(r):
                break
            elif item.overlap(r):
                try:
                    self._list[i] = r.difference(item)

                    # If the element becomes empty remove it entirely
                    if not self._list[i]:
                        del self._list[i]
                        continue
                except ValueError:
                    # The range was within the range, causing it to be split so
                    # we do this split manually
                    del self._list[i]
                    self._list.insert(
                        i, r.replace(lower=item.upper, lower_inc=not item.upper_inc))
                    self._list.insert(
                        i, r.replace(upper=item.lower, upper_inc=not item.lower_inc))

                    # When this happens we know we are done
                    break
            i += 1

    def span(self):
        """
        Return a range that spans from the first point to the last point in this
        set. This means the smallest range containing all elements of this set
        with no gaps.

            >>> intrangeset([intrange(1, 5), intrange(30, 40)]).span()
            intrange([1,40))

        :return: A new range the contains this entire range set.
        """

        # If the set is empty we treat it specially by returning an empty range
        if not self:
            return self.type.empty()

        return self._list[0].replace(
            upper=self._list[-1].upper,
            upper_inc=self._list[-1].upper_inc)

    def union(self, *others):
        """
        Returns this set combined with every given set into a super set for each
        given set.

            >>> intrangeset([intrange(1, 5)]).union(
            ...     intrangeset([intrange(5, 10)]))
            intrangeset([intrange([1,10))])

        :param other: Range set to merge with.
        :return: A new range set that is the union of this and `other`.
        """

        # Make a copy of self and add all its ranges to the copy
        union = self.copy()
        for other in others:
            for r in other:
                union.add(r)
        return union

    def difference(self, *others):
        """
        Returns this set stripped of every subset that are in the other given
        sets.

            >>> intrangeset([intrange(1, 15)]).difference(
            ...     intrangeset([intrange(5, 10)]))
            intrangeset([intrange([1,5)), intrange([10,15))])

        :param other: Range set to compute difference against.
        :return: A new range set that is the difference between this and `other`.
        """

        # Make a copy of self and remove all its ranges from the copy
        difference = self.copy()
        for other in others:
            for r in other:
                difference.remove(r)
        return difference

    def intersection(self, *others):
        """
        Returns a new set of all subsets that exist in this and every given set.

            >>> intrangeset([intrange(1, 15)]).intersection(
            ...     intrangeset([intrange(5, 10)]))
            intrangeset([intrange([5,10))])

        :param other: Range set to intersect this range set with.
        :return: A new range set that is the intersection between this and
                 `other`.
        """

        # Initialize output with a reference to this rangeset. When
        # intersecting against multiple rangesets at once this will be replaced
        # after each iteration.
        output = self

        for other in others:
            # Intermediate rangeset containing intersection for this current
            # iteration.
            intersection = self.__class__([])

            # Intersect every range within the current output with every range
            # within the currently processed other rangeset. All intersecting
            # parts are added to the intermediate intersection set.
            for a in output:
                for b in other:
                    intersection.add(a.intersection(b))

            # If the intermediate intersection rangeset is still empty, there
            # where no intersections with at least one of the arguments and
            # we can quit early, since any intersection with the empty set will
            # always be empty.
            if not intersection:
                return intersection

            # Update output with intersection for the current iteration.
            output = intersection

        return output

    __contains__ = contains

    # Some operators that set() has:
    # TODO: Use NotImplemented
    __or__ = union
    __and__ = intersection
    __sub__ = difference

    # Python 3 support
    __bool__ = __nonzero__


class intrangeset(rangeset):
    """
    Range set that operates on intranges.

        >>> intrangeset([intrange(1, 5), intrange(10, 15)])
        intrangeset([intrange([1,5)), intrange([10,15))])

    Inherits methods from :class:`~spans.settypes.rangeset`,
    :class:`~spans.settypes.discreterangeset` and
    :class:`~spans.settypes.offsetablerangeset`.

    See also :class:`~spans.types.intrange`.
    """

    __slots__ = ()

    type = intrange


class floatrangeset(rangeset):
    """
    Range set that operates on floatranges.

        >>> floatrangeset([floatrange(1.0, 5.0), floatrange(10.0, 15.0)])
        floatrangeset([floatrange([1.0,5.0)), floatrange([10.0,15.0))])

    Inherits methods from :class:`~spans.settypes.rangeset`,
    :class:`~spans.settypes.discreterangeset` and
    :class:`~spans.settypes.offsetablerangeset`.

    See also :class:`~spans.types.floatrange`.
    """

    __slots__ = ()

    type = floatrange


class strrangeset(rangeset):
    """
    Range set that operates on strranges.

        >>> strrangeset([
        ...     strrange(u"a", u"f", upper_inc=True),
        ...     strrange(u"0", u"9", upper_inc=True)])
        strrangeset([strrange([u'0',u':')), strrange([u'a',u'g'))])

    Inherits methods from :class:`~spans.settypes.rangeset` and
    :class:`~spans.settypes.discreterangeset`.

    See also :class:`~spans.types.strrange`.
    """

    __slots__ = ()

    type = strrange


class daterangeset(rangeset):
    """
    Range set that operates on dateranges.

        >>> month = daterange(date(2000, 1, 1), date(2000, 2, 1))
        >>> daterangeset([month, month.offset(timedelta(366))]) # doctest: +NORMALIZE_WHITESPACE
        daterangeset([daterange([datetime.date(2000, 1, 1),datetime.date(2000, 2, 1))),
            daterange([datetime.date(2001, 1, 1),datetime.date(2001, 2, 1)))])

    Inherits methods from :class:`~spans.settypes.rangeset`,
    :class:`~spans.settypes.discreterangeset` and
    :class:`~spans.settypes.offsetablerangeset`.

    See also :class:`~spans.types.daterange`.
    """

    __slots__ = ()

    type = daterange


class datetimerangeset(rangeset):
    """
    Range set that operates on datetimeranges.

        >>> month = datetimerange(datetime(2000, 1, 1), datetime(2000, 2, 1))
        >>> datetimerangeset([month, month.offset(timedelta(366))]) # doctest: +NORMALIZE_WHITESPACE
        datetimerangeset([datetimerange([datetime.datetime(2000, 1, 1, 0, 0),datetime.datetime(2000, 2, 1, 0, 0))),
            datetimerange([datetime.datetime(2001, 1, 1, 0, 0),datetime.datetime(2001, 2, 1, 0, 0)))])

    Inherits methods from :class:`~spans.settypes.rangeset` and
    :class:`~spans.settypes.offsetablerangeset`.

    See also :class:`~spans.types.datetimerange`.
    """

    __slots__ = ()

    type = datetimerange


class timedeltarangeset(rangeset):
    """
    Range set that operates on timedeltaranges.

        >>> week = timedeltarange(timedelta(0), timedelta(7))
        >>> timedeltarangeset([week, week.offset(timedelta(7))])
        timedeltarangeset([timedeltarange([datetime.timedelta(0),datetime.timedelta(14)))])

    Inherits methods from :class:`~spans.settypes.rangeset` and
    :class:`~spans.settypes.offsetablerangeset`.

    See also :class:`~spans.types.timedeltarange`.
    """

    __slots__ = ()

    type = timedeltarange
