Welcome to Spans' documentation!
================================
Spans is a pure Python implementation of PostgreSQL's
`range types <http://www.postgresql.org/docs/9.2/static/rangetypes.html>`_.
Range types are conveinent when working with intervals of any kind. Every time
you've found yourself working with date_start and date_end, an interval may have
been what you were actually looking for.

Spans has successfully been used in production since its first release
30th August, 2013.


Example
-------
Imagine you are building a calendar and want to display all weeks that overlaps
the current month. Normally you have to do some date trickery to achieve this,
since the month's bounds may be any day of the week. With Spans' set-like
operations and shortcuts the problem becomes a breeze.

We start by importing ``date`` and ``daterange``

.. code-block:: python

    >>> from datetime import date
    >>> from spans import daterange

Using ``daterange.from_month`` we can get range representing January in the year
2000

.. code-block:: python

    >>> month = daterange.from_month(2000, 1)
    >>> month
    daterange([datetime.date(2000, 1, 1),datetime.date(2000, 2, 1)))

Now we can calculate the ranges for the weeks where the first and last day of
month are

.. code-block:: python

    >>> start_week = daterange.from_date(month.lower, period="week")
    >>> end_week = daterange.from_date(month.last, period="week")
    >>> start_week
    daterange([datetime.date(1999, 12, 27),datetime.date(2000, 1, 3)))
    >>> end_week
    daterange([datetime.date(2000, 1, 31),datetime.date(2000, 2, 7)))

Using a union we can express the calendar view.

.. code-block:: python

    >>> start_week.union(month).union(end_week)
    daterange([datetime.date(1999, 12, 27),datetime.date(2000, 2, 7)))


Introduction
------------

.. toctree::
   :maxdepth: 2

   introduction
   ranges
   custom_types
   recipes
   api
   changelog
