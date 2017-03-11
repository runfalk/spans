Ranges
======
Ranges are like `intervals in mathematics <https://en.wikipedia.org/wiki/Interval_%28mathematics%29>`_. They have a start and end. Every value between the enpoints is included in the range. Integer ranges (:class:`~spans.types.intrange`) will be used for all examples. Built in range types are listed in `Available range types`_.

A simple range:

.. code-block:: python

	>>> span = intrange(1, 5)
	>>> span.lower
	1
	>>> span.upper
	5

By default all ranges include all elements from and including `lower` up to but not including `upper`. This means that the last element included in the discrete :class:`~spans.types.intrange` is `4`.

.. code-block:: python

	>>> intrange(1, 5).last
	4

Non discrete ranges, such as :class:`~spans.types.floatrange`, do not have the property last :class:`~spans.types.discreterange.last`.

Discrete ranges are always normalized, while normal ranges are not.

.. code-block:: python

	>>> intrange(1, 5, upper_inc=True)
	intrange([1,6))
	>>> floatrange(1.0, 5.0, upper_inc=True)
	floatrange([1.0,5.0])

The ``__repr__`` for ranges follows the same format as used by PostgreSQL's ranges. ``[`` and ``]`` means that the boundaries are included in the range and ``(`` and ``)`` means that they are not.

Ranges support set operations such as :class:`~spans.types.range_.union`, :class:`~spans.types.range_.difference` and :class:`~spans.types.range_.intersection`.

.. code-block:: python

	>>> intrange(1, 5).union(intrange(5, 10))
	intrange([1,10))
	>>> intrange(1, 10).difference(intrange(5, 15))
	intrange([1,5))
	>>> intrange(1, 10).intersection(intrange(5, 15))
	intrange([5,10))

Unions and differences that would result in two sets will result in a ``ValueError``. To perform such operations `Range sets`_ must be used.

.. code-block:: python

	>>> intrange(1, 5).union(intrange(10, 15))
	Traceback (most recent call last):
	  File "<stdin>", line 1, in <module>
	ValueError: Ranges must be either adjacent or overlapping

.. note::
	This behavior is for consistency with PostgreSQL.

Available range types
---------------------
The following range types are built in:

- Integer range (:class:`~spans.types.intrange`)
- Float range (:class:`~spans.types.floatrange`)
- String range (:class:`~spans.types.strrange`) which operate on unicode strings
- Date range (:class:`~spans.types.daterange`)
- Datetime range (:class:`~spans.types.datetimerange`)
- Timedelta range (:class:`~spans.types.timedeltarange`)

Range sets
----------
Range sets are sets of intervals, where each element must be represented by one and only one range. Range sets are the solution to the problem when an operation will result in two separate ranges.

.. code-block:: python

	>>> intrangeset([intrange(1, 5), intrange(10, 15)])
	intrangeset([intrange([1,5)), intrange([10,15))])

Like ranges, range sets support :class:`~spans.settypes.rangeset.union`, :class:`~spans.settypes.rangeset.difference` and :class:`~spans.settypes.rangeset.intersection`. Contrary to Python's built in sets these operations do not modify the range set in place. Instead it returns a new set. Unchanged ranges are reused to conserve memory since ranges are immutable.

Range sets are however mutable structures. To modify an existing set in place the :class:`~spans.settypes.rangeset.add` and :class:`~spans.settypes.rangeset.remove` methods are used.

.. code-block:: python

	>>> span = intrangeset([intrange(1, 5)])
	>>> span.add(intrange(5, 10))
	>>> span
	intrangeset([intrange([1,10))])
	>>> span.remove(intrange(3, 7))
	>>> span
	intrangeset([intrange([1,3)), intrange([7,10))])



