Welcome to Spans' documentation!
================================
Spans is a pure Python implementation of PostgreSQL's range types [#]_. Range types are conveinent when working with intervals of any kind. Every time you've found yourself working with ``date_start`` and ``date_end``, an interval like Spans' range may have been what you were actually looking for.

Spans also provide a more flexible way of working with ranges with the range set classes.

.. [#] http://www.postgresql.org/docs/9.2/static/rangetypes.html

Introduction
------------

.. toctree::
   :maxdepth: 2

   introduction
   ranges
   custom_types
   api
   changelog
