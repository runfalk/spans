Changelog
=========
Version are structured like the following: ``<major>.<minor>.<bugfix>``. The
first `0.1` release does not properly adhere to this. Unless explicitly stated,
changes are made by `Andreas Runfalk <https://github.com/runfalk>`_.

Version 0.4.0
-------------
Released on 20th March, 2017

- Added new argument to :meth:`~spans.types.daterange.from_date` for working
  with different kinds of date intervals. The argument accepts a period of either
  ``"day"`` (default), ``"week"`` (ISO week), ``"american_week"`` (starts on
  sunday), ``"month"``, ``"quarter"`` or ``"year"``.
- Added new methods to :class:`~spans.types.daterange` for working with different
  kinds of date intervals:
  :meth:`~spans.types.daterange.from_week`,
  :meth:`~spans.types.daterange.from_month`,
  :meth:`~spans.types.daterange.from_quarter` and
  :meth:`~spans.types.daterange.from_year`.
- Added a new class :class:`~spans.types.PeriodRange` for working with periods
  like weeks, months, quarters or years. It inherits all methods from
  :class:`~spans.types.daterange` and is aware of its own period type. It
  allows things like getting the previous or next week.
- Fixed :class:`~spans.types.daterange` not accepting subclasses of ``date``
  (`bug #5 <https://github.com/runfalk/spans/issues/5>`_)
- Fixed some broken doctests
- Moved unit tests to `pytest <http://docs.pytest.org/en/latest/>`_
- Removed `Tox <https://tox.readthedocs.io/en/latest/>`_ config
- Minor documentation tweaks

Version 0.3.0
-------------
Released on 26th August, 2016

- Added documentation for :meth:`~spans.settypes.rangeset.__iter__`
- Fixed intersection of multiple range sets not working correctly
  (`bug #3 <https://github.com/runfalk/spans/issues/3>`_)
- Fixed iteration of :class:`~spans.settypes.rangeset` returning an empty range
  when ``rangeset`` is empty
  (`bug #4 <https://github.com/runfalk/spans/issues/4>`_)

.. warning::
   This change is backwards incompatible to code that expect rangesets to always
   return at least one set when iterating.

Version 0.2.1
-------------
Released on 27th June, 2016

- Fixed :class:`~spans.settypes.rangeset` not returning ``NotImplemented`` when
  comparing to classes that are not sub classes of ``rangeset``, pull request
  `#2 <https://github.com/runfalk/spans/pull/2>`_
  (`Michael Krahe <https://github.com/der-michik>`_)
- Updated license in ``setup.py`` to follow
  `recommendations <https://packaging.python.org/en/latest/distributing/#license>`_
  by PyPA

Version 0.2.0
-------------
Released on 22nd December, 2015

- Added :meth:`~spans.settypes.rangeset.__len__` to range sets
  (`Michael Krahe <https://github.com/der-michik>`_)
- Added :meth:`~spans.settypes.rangeset.contains` to range sets
  (`Michael Krahe <https://github.com/der-michik>`_)
- Added `Sphinx <http://sphinx-doc.org/>`_ style doc strings to all methods
- Added proper Sphinx documentation
- Added unit tests for uncovered parts, mostly error checking
- Added `wheel <https://www.python.org/dev/peps/pep-0427/>`_ to PyPI along with
  source distribution
- Fixed a potential bug where comparing ranges of different types would result
  in an infinite loop
- Changed meta class implementation for range sets to allow more mixins for
  custom range sets

Version 0.1.4
-------------
Released on 15th May, 2015

- Added :attr:`~spans.types.discreterange.last` property to
  :class:`~spans.types.discreterange`
- Added :meth:`~spans.types.daterange.from_date` helper to
  :class:`~spans.types.daterange`
- Added more unit tests
- Improved pickle implementation
- Made type checking more strict for date ranges to prevent ``datetime`` from
  being allowed in :class:`~spans.types.daterange`

Version 0.1.3
-------------
Released on 27th February, 2015

- Added :meth:`~spans.types.offsetablerange.offset` to some range types
- Added :meth:`~spans.settypes.offsetablerangeset.offset` to some range set types
- Added sanity checks to range boundaries
- Fixed incorrect ``__slots__`` usage, resulting in ``__slots__`` not being used
  on most ranges
- Fixed pickling of ranges and range sets
- Simplified creation of new rangesets, by the use of the meta class
  ``metarangeset``

Version 0.1.2
-------------
Released on 13th June, 2014

- Fix for inproper version detection on Ubuntu's bundled Python interpreter

Version 0.1.1
-------------
Released on 12th June, 2014

- Readme fixes
- Syntax highlighting for PyPI page

Version 0.1.0
-------------
Released on 30th August, 2013

- Initial release
