Changelog
=========
Version are structured like the following: ``<major>.<minor>.<bugfix>``. The
first `0.1` release does not properly adhere to this. Unless explicitly stated,
changes are made by `Andreas Runfalk <https://github.com/runfalk>`_.

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
