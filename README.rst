Spans
=====
|test-status| |test-coverage| |documentation-status| |pypi-version|

Spans is a pure Python implementation of PostgreSQL's range types [#]_. Range types
are conveinent when working with intervals of any kind. Every time you've found
yourself working with date_start and date_end, an interval may have been what
you were actually looking for.

Spans has successfully been used in production since its first release
30th August, 2013.

Here is an example on how to use ranges to determine if something happened in
the 90s.

.. code-block:: python

    >>> from spans import daterange
    >>> from datetime import date
    >>> the90s = daterange(date(1990, 1, 1), date(2000, 1, 1))
    >>> date(1996, 12, 4) in the90s
    True
    >>> date(2000, 1, 1) in the90s
    False
    >>> the90s.union(daterange(date(2000, 1, 1), date(2010, 1, 1)))
    daterange([datetime.date(1990, 1, 1), datetime.date(2010, 1, 1))))

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

.. code-block:: bash

    $ pip install Spans

Documentation
-------------
`Documentation <http://spans.readthedocs.org/en/latest/>`_ is hosted on Read the
Docs.

Use with Psycopg2
-----------------
To use these range types with Psycopg2 the PsycoSpans library exists [#]_.

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
.. [#] https://www.github.com/runfalk/psycospans

.. |test-status| image:: https://travis-ci.org/runfalk/spans.svg
    :alt: Test status
    :scale: 100%
    :target: https://travis-ci.org/runfalk/spans

.. |test-coverage| image:: https://codecov.io/github/runfalk/spans/coverage.svg?branch=master
    :alt: Test coverage
    :scale: 100%
    :target: https://codecov.io/github/runfalk/spans?branch=master

.. |documentation-status| image:: https://readthedocs.org/projects/spans/badge/
    :alt: Documentation status
    :scale: 100%
    :target: http://spans.readthedocs.org/en/latest/

.. |pypi-version| image:: https://badge.fury.io/py/spans.svg
    :alt: PyPI version status
    :scale: 100%
    :target: https://pypi.python.org/pypi/Spans/

.. Include changelog on PyPI

.. include:: doc/changelog.rst
