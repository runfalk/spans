Spans
=====
|test-status| |test-coverage| |documentation-status| |pypi-version| |py-versions| |license|

Spans is a pure Python implementation of PostgreSQL's
`range types <http://www.postgresql.org/docs/9.2/static/rangetypes.html>`_.
Range types are conveinent when working with intervals of any kind. Every time
you've found yourself working with date_start and date_end, an interval may have
been what you were actually looking for.

Spans has successfully been used in production since its first release
30th August, 2013.


Installation
------------
Spans exists on PyPI.

.. code-block:: bash

    $ pip install Spans

`Documentation <http://spans.readthedocs.org/en/latest/>`_ is hosted on Read the
Docs.


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

Do you want to know more? Head over to the
`documentation <http://spans.readthedocs.org/en/latest/>`_.


Use with Psycopg2
-----------------
To use these range types with Psycopg2 the
`PsycoSpans <https://www.github.com/runfalk/psycospans>`_.


Motivation
----------
For a project of mine I started using PostgreSQL's ``tsrange`` type and needed
an equivalent in Python. These range types attempt to mimick PostgreSQL's
behavior in every way. Deviating from it is considered as a bug and should be
reported.


Contribute
----------
I appreciate all the help I can get! Some things to think about:

- If it's a simple fix, such as documentation or trivial bug fix, please file
  an issue or submit a pull request. Make sure to only touch lines relevant to
  the issue. I don't accept pull requests that simply reformat the code to be
  PEP8-compliant. To me the history of the repository is more important.
- If it's a feature request or a non-trivial bug, always open an issue first to
  discuss the matter. It would be a shame if good work went to waste because a
  pull request doesn't fit the scope of this project.

Pull requests are credited in the change log which is displayed on PyPI and the
documentaion on Read the Docs.


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

.. |pypi-version| image:: https://badge.fury.io/py/Spans.svg
    :alt: PyPI version status
    :scale: 100%
    :target: https://pypi.python.org/pypi/Spans/

.. |py-versions| image:: https://img.shields.io/pypi/pyversions/Spans.svg
    :alt: Python version
    :scale: 100%
    :target: https://pypi.python.org/pypi/Spans/

.. |license| image:: https://img.shields.io/github/license/runfalk/spans.svg
    :alt: MIT License
    :scale: 100%
    :target: https://github.com/runfalk/spans/blob/master/LICENSE

.. Include changelog on PyPI

.. include:: doc/changelog.rst
