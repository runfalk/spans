PostgreSQL analogies
====================
This page describes range types, functions and operators in PostgreSQL, and what
their Spans equivalents are.


Range types
-----------
Most range types included in Spans have an equivalent in PostgreSQL.

==================================  ==================================================================================================
Postgresql type                     Python type
==================================  ==================================================================================================
``int4range``                       :class:`~spans.types.intrange`
``int8range``                       :class:`~spans.types.intrange`
``numrange``                        :class:`~spans.types.floatrange`, though :class:`~spans.types.floatrange` does not accept integers
``tsrange``                         :class:`~spans.types.datetimerange`
``tstzrange``                       :class:`~spans.types.datetimerange`
``daterange``                       :class:`~spans.types.daterange`
`Does not exist` [#intervalrange]_  :class:`~spans.types.timedeltarange`
`Does not exist`                    :class:`~spans.types.strrange`
==================================  ==================================================================================================


Operators
---------
Most operators are not overloaded in Python to their PostgreSQL equivalents.
Instead Spans implements the functionality using methods.

===============================  ========================  ==================================
Operator                         PostgreSQL                Python
===============================  ========================  ==================================
Equal                            ``a = b``                 ``a == b``
Not equal                        ``a != b`` or ``a <> b``  ``a != b``
Less than                        ``a < b``                 ``a < b``
Greater than                     ``a > b``                 ``a > b``
Less than or equal               ``a < b``                 ``a < b``
Greater than or equal            ``a > b``                 ``a > b``
Contains                         ``a @> b``                ``a.contains(b)``
Is contained by                  ``a <@ b``                ``a in b`` or ``a.within(b)``
Overlap                          ``a && b``                ``a.overlap(b)``
Strictly left of                 ``a << b``                ``a.left_of(b)`` or ``a << b``
Strictly right of                ``a >> b``                ``a.right_of(b)`` or ``a >> b``
Does not extend to the right of  ``a &< b``                ``a.endsbefore(b)``
Does not extend to the left of   ``a &> b``                ``a.startsafter(b)``
Is adjacent to                   ``a -|- b``               ``a.adjacent(b)``
Union                            ``a + b``                 ``a.union(b)`` or ``a | b``
Intersection                     ``a * b``                 ``a.intersection(b)`` or ``a & b``
Difference                       ``a - b``                 ``a.difference(b)`` or ``a - b``
===============================  ========================  ==================================


Functions
---------
There are no functions in Spans that operate on ranges. Instead they are
implemented as methods, properties or very simple combinations.

===================  ==============================
PostgreSQL function  Python equivalent
===================  ==============================
``lower(a)``         ``a.lower``
``upper(a)``         ``a.upper``
``isempty(a)``       ``a.upper``
``lower_inc(a)``     ``a.lower_inc``
``upper_inc(a)``     ``a.upper_inc``
``lower_inf(a)``     ``a.lower_inf``
``upper_inf(a)``     ``a.upper_inf``
``range_merge(a)``   ``intrangeset([a, b]).span()``
===================  ==============================


.. [#intervalrange] Though it is not built in it can be created using:
                    ``CREATE TYPE intervalrange AS RANGE(SUBTYPE = interval);``
