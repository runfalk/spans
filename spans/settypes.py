from functools import total_ordering
from itertools import chain

from .types import range_
from .types import *

__all__ = [
    "intrangeset",
    "floatrangeset",
    "strrangeset",
    "daterangeset",
    "datetimerangeset",
    "timedeltarangeset"
]

@total_ordering
class rangeset(object):
    __slots__ = ("_list")

    def __init__(self, ranges):
        self._list = [self.type.empty()]

        for r in ranges:
            self.add(r)

    def __repr__(self):
        if not self:
            return "{0.__class__.__name__}([])".format(self)
        else:
            return "{instance.__class__.__name__}({list!r})".format(
                instance=self,
                list=self._list)

    def __nonzero__(self):
        """
        Returns False if the only thing in this set is the empty set, otherwise
        it returns True.

            >>> bool(intrangeset([]))
            False
            >>> bool(intrangeset([intrange(1, 5)]))
            True

        """
        return bool(len(self._list) != 1 or self._list[0])

    def __iter__(self):
        return iter(self._list)

    def __eq__(self, other):
        return self._list == other._list

    def __lt__(self, other):
        return self._list < other._list

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

        """

        return self.__class__(self)

    def add(self, item):
        """
        Adds a range to the set. This operation updates the set in place.

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

        """

        self._test_type(item)

        # If item is empty, do not add it
        if not item:
            return

        # If the list currently only have an empty range in it replace it by this
        # item
        if not self:
            self._list = [item]
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

        """

        # If the list currently only have an empty range do nothing
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

        # If the list was wiped clean we must at least have the empty range in it
        if not self._list:
            self._list.append(self.type.empty())

    def span(self):
        """
        Return a range that spans from the first point to the last point in this
        set. This means the smallest range containing all elements of this set
        with no gaps.

            >>> intrangeset([intrange(1, 5), intrange(30, 40)]).span()
            intrange([1,40))

        """

        # If the list is empty we treat it specially by returning an empty range
        if not self:
            return self._list[0]

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

        """

        # TODO: Optimize this

        intersection = self.__class__([])
        for other in others:
            for a in self:
                for b in other:
                    intersection.add(a.intersection(b))
        return intersection

    # Some operators that set() has:
    # TODO: Use NotImplemented
    __or__ = union
    __and__ = intersection
    __sub__ = difference

    # Python 3 support
    __bool__ = __nonzero__

class discreterangeset(rangeset):
    __slots__ = ()

    def values(self):
        """
        Returns an iterator going through each value in this range set.

            >>> list(intrangeset([intrange(1, 5), intrange(10, 15)]).values())
            [1, 2, 3, 4, 10, 11, 12, 13, 14]

        """

        return chain(*self)

class intrangeset(discreterangeset):
    __slots__ = ()

    type = intrange

class floatrangeset(rangeset):
    __slots__ = ()

    type = floatrange

class strrangeset(discreterangeset):
    __slots__ = ()

    type = strrange

class daterangeset(discreterangeset):
    __slots__ = ()

    type = daterange

class datetimerangeset(rangeset):
    __slots__ = ()

    type = datetimerange

class timedeltarangeset(rangeset):
    __slots__ = ()

    type = timedeltarange
