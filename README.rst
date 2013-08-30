Spans
=====
Spans is a pure Python implementation of PostgreSQL's range types [#]_. Range types
are conveinent when working with intervals of any kind. Every time you've found
yourself working with date_start and date_end, an interval may have been what
you were looking for.

If you are making a booking application for a bed and breakfast hotel and want
to ensure no room gets double booked:

.. code-block:: python

    from collections import defaultdict
    from datetime import date
    from spans import daterange

    # Add a booking from 2013-01-14 through 2013-01-15
    bookings = defaultdict(list, {
        1 : [daterange(date(2013, 1, 14), date(2013, 1, 16))]
    }

    def is_valid_booking(bookings, room, new_booking):
        return not any(booking.overlap(new_booking for booking in bookings[room])

    print is_valid_booking(
        bookings, 1, daterange(date(2013, 1, 14), date(2013, 1, 18))) # False
    print is_valid_booking(
        bookings, 1, daterange(date(2013, 1, 16), date(2013, 1, 18))) # True

The library supports ranges and sets of ranges. A ``range`` has no discontinuities
between its endpoints. For some applications this is a requirement and hence the
``rangeset`` type exists.

Apart from the above mentioned overlap operation; ranges support ``union``,
``difference``, ``intersection``, ``contains``, ``startswith``, ``endswith``,
``left_of`` and ``right_of``.

Built-in ranges:

- ``intrange``
- ``floatrange``
- ``strrangerange`` - For ``unicode`` strings
- ``daterange``
- ``datetimerange``
- ``timedeltarange``

For each one of the ``range`` types a ``rangeset`` type exists as well:

- ``intrangeset``
- ``floatrangeset``
- ``strrangerangeset``
- ``daterangeset``
- ``datetimerangeset``
- ``timedeltarangeset``

Motivation
----------
For a recent project of mine I started using PostgreSQL's ``tsrange`` type and
needed an equivalent in Python. These range types attempt to mimick PostgreSQL's
behavior in every way. Deviating from it is considered as a bug and should be
reported.

Installation
------------

Spans exists on PyPI.

::

    pip install Spans

Documentation
-------------
For full doumentation please run ``pydoc spans`` from a shell.

Custom range types
------------------
Using your own types for ranges are easy, just extend a base class and you're
good to go:

.. code-block:: python

    from spans.types import range_, discreterange
    from spans.settypes import rangeset, discreterangeset

    class intrange(discreterange):
        __slots__ = ()
        type = int
        step = 1

    class intrangeset(discreterangeset):
        __slots__ = ()
        type = intrange

    class floatrange(range_):
        __slots__ = ()
        type = float

    class floatrangeset(rangeset):
        __slots__ = ()
        type = floatrange

For a deeper set of examples please refer to ``types.py`` and ``settypes.py``.

.. [#] http://www.postgresql.org/docs/9.2/static/rangetypes.html
