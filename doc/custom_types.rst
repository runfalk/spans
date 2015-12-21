Custom range types
==================
The built in range types may not suffice for your particular application. It is very easy to extend with your own classes. The only requirement is that the type supports rich comparison :pep:`207` and is immutable.

Standard range types
--------------------
A normal range can be implemented by extending :class:`spans.types.range_`.

.. code-block:: python

	from spans.types import range_

	class floatrange(range_):
		__slots__ = ()
		type = float

	span = floatrange(1.0, 5.0)

	assert span.lower == 1.0
	assert span.upper == 5.0

.. note::
	The ``__slots__ = ()`` is a performance optimization that is used for all ranges. It lowers the memory footprint for every instance. It is not mandatory but encourgaged.

Offsetable range types
----------------------
An offsetable range can be implemented using the mixin :class:`spans.types.offsetablerange`. The class still needs to extend :class:`spans.types.range_`.

.. code-block:: python

	from spans.types import range_, offsetablerange

	class floatrange(range_, offsetablerange):
		__slots__ = ()
		type = float

If the offset type is not the same as the range type (such as ``date`` that is offsetable with ``timedelta``) the attribute ``offset_type`` can be used.

.. code-block:: python

	from spans.types import discreterange, offsetablerange
	from datetime import date, timedelta

	class daterange(discreterange, offsetablerange):
		__slots__ = ()

		type = date
		offset_type = timedelta

	span = daterange(date(2000, 1, 1), date(2000, 2, 1))
	assert span.offset(timedelta(14)).upper == date(2000, 2, 15)

Discrete range types
--------------------
Discrete ranges (such as :class:`~spans.types.intrange` and :class:`~spans.types.daterange`) can be implemented by extending :class:`spans.types.discreterange`.

.. code-block:: python

	from spans.types import discreterange, offsetablerange

	class intrange(discreterange, offsetablerange):
		__slots__ = ()
		type = intrange
		step = 1

	assert list(intrange(1, 5)) == [1, 2, 3, 4]

Note the `step` attribute. It must always be the smallest possible unit. Using `2` for intranges would not have expected behavior.

Range sets
----------
Range sets are conveinient to implement regardless of the mixins used. This is due to the metaclass

.. code-block:: python

	from spans.types import intrange
	from spans.settypes import rangeset

	class intrangeset(rangetset):
		__slots__ = ()
		type = intrange

	assert intrangeset(
		[intrange(1, 5), intrange(10, 15)]).span() == intrange(1, 15)

Custom mixins
-------------
It is possible to create custom mixins for range sets by adding mappings to :class:`spans.settypes.metarangeset`. The mapping has to be added before the range set class is created or it will not be used.
