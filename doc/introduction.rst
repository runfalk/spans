Introduction
============
For a recent project of mine I started using PostgreSQL's ``tsrange`` type and needed an equivalent in Python. These range types attempt to mimick PostgreSQL's behavior in every way. To make ranges more useful some extra methods have been added that are not available in PostgreSQL.

Requirements
------------
Spans have no requirements but the standard library. It is known to work on the following Python versions

- Python 2.7
- Python 3.3
- Python 3.4
- Python 3.5
- Python 3.6
- PyPy

It may work on other version as well.

Installation
------------
Spans is available from `PyPI <https://pypi.python.org/pypi/Spans/>`_.

.. code-block:: bash

    $ pip install spans


Example
-------
If you are making a booking application for a bed and breakfast hotel and want
to ensure no room gets double booked:

.. code-block:: python
   :linenos:

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


Using with Psycopg
------------------
To use Spans with `Psycopg <http://initd.org/psycopg/>`_ the `Psycospans <https://github.com/runfalk/psycospans>`_ project exists.
