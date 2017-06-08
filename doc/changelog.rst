Changelog
=========
Version are structured like the following: ``<major>.<minor>.<bugfix>``. The
first `0.1` release does not properly adhere to this. Unless explicitly stated,
changes are made by `Andreas Runfalk <https://github.com/runfalk>`_.


Version 1.0.0
-------------
Released on 8th June, 2017

- Added ``NotImplemented`` for ``<<`` and ``>>`` operators when there is a type
  mismatch
- Added ``|`` operator for unions of :class:`~spans.types.Range` and
  ``NotImplemented`` support for :class:`~spans.settypes.RangeSet`
- Added ``&`` operator for intersections of :class:`~spans.types.Range` and
  ``NotImplemented`` support for :class:`~spans.settypes.RangeSet`
- Added ``-`` operator for differences of :class:`~spans.types.Range` and
  ``NotImplemented`` support for :class:`~spans.settypes.RangeSet`
- Added ``reversed()`` iterator support for :class:`~spans.types.DiscreteRange`
- Fixed overlap with empty range incorrectly returns ``True``
  (`bug #7 <https://github.com/runfalk/spans/issues/7>`_)
- Fixed issue with :meth:`~spans.types.Range.contains` for scalars on unbounded
  ranges
- Fixed type check for :meth:`~spans.types.Range.right_of`
- Fixed type check for :meth:`~spans.settypes.RangeSet.contains`
- Fixed type check for :meth:`~spans.settypes.RangeSet.union`
- Fixed type check for :meth:`~spans.settypes.RangeSet.intersection`
- Fixed type check for :meth:`~spans.settypes.RangeSet.difference`
- Fixed infinite iterators not being supported for
  :class:`~spans.types.DiscreteRange`


Version 0.5.0
-------------
Released on 16th April, 2017

This release is a preparation for a stable 1.0 release.

- Fixed comparison operators when working with empty or unbounded ranges. They
  would previously raise exceptions. Ranges are now partially ordered instead of
  totally ordered
- Added more unit tests
- Renamed classes to match :pep:`8#class-names` conventions. This does not apply
  to classes that works on built-in that does not follow :pep:`8#class-names`.
- Refactored :meth:`~spans.types.Range.left_of`
- Refactored :meth:`~spans.types.Range.overlap`
- Refactored :meth:`~spans.types.Range.union`


Version 0.4.0
-------------
Released on 20th March, 2017

This release is called 0.4.1 on PyPI because I messed up the upload.

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

- Added documentation for :meth:`~spans.settypes.RangeSet.__iter__`
- Fixed intersection of multiple range sets not working correctly
  (`bug #3 <https://github.com/runfalk/spans/issues/3>`_)
- Fixed iteration of :class:`~spans.settypes.RangeSet` returning an empty range
  when ``RangeSet`` is empty
  (`bug #4 <https://github.com/runfalk/spans/issues/4>`_)

.. warning::
   This change is backwards incompatible to code that expect range sets to
   always return at least one set when iterating.


Version 0.2.1
-------------
Released on 27th June, 2016

- Fixed :class:`~spans.settypes.RangeSet` not returning ``NotImplemented`` when
  comparing to classes that are not sub classes of ``RangeSet``, pull request
  `#2 <https://github.com/runfalk/spans/pull/2>`_
  (`Michael Krahe <https://github.com/der-michik>`_)
- Updated license in ``setup.py`` to follow
  `recommendations <https://packaging.python.org/en/latest/distributing/#license>`_
  by PyPA


Version 0.2.0
-------------
Released on 22nd December, 2015

- Added :meth:`~spans.settypes.RangeSet.__len__` to range sets
  (`Michael Krahe <https://github.com/der-michik>`_)
- Added :meth:`~spans.settypes.RangeSet.contains` to range sets
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

- Added :attr:`~spans.types.DiscreteRange.last` property to
  :class:`~spans.types.DiscreteRange`
- Added :meth:`~spans.types.daterange.from_date` helper to
  :class:`~spans.types.daterange`
- Added more unit tests
- Improved pickle implementation
- Made type checking more strict for date ranges to prevent ``datetime`` from
  being allowed in :class:`~spans.types.daterange`


Version 0.1.3
-------------
Released on 27th February, 2015

- Added :meth:`~spans.types.OffsetableRangeMixin.offset` to some range types
- Added :meth:`~spans.settypes.OffsetableRangeSetMixin.offset` to some range set
  types
- Added sanity checks to range boundaries
- Fixed incorrect ``__slots__`` usage, resulting in ``__slots__`` not being used
  on most ranges
- Fixed pickling of ranges and range sets
- Simplified creation of new range sets, by the use of the meta class
  :class:`~spans.settypes.MetaRangeSet`


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
