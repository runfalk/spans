.. module:: spans

API documentation
=================
This is the API reference for all public classes and functions in Spans.

Ranges
------
Range class
~~~~~~~~~~~
The ``range_`` class is the base for all ranges. Since this is an abstract class all examples uses the :class:`.intrange` sub class. The name ``range_`` with the trailing underscore is used to prevent overwriting the built in ``range`` (in compliance with :pep:`8`.)

.. autoclass:: spans.types.range_
   :members:

Discrete range
~~~~~~~~~~~~~~
.. autoclass:: spans.types.discreterange
   :members:

Offsetable range
~~~~~~~~~~~~~~~~
.. autoclass:: spans.types.offsetablerange
   :members: offset

Integer range
~~~~~~~~~~~~~
.. autoclass:: spans.types.intrange

Float range
~~~~~~~~~~~
.. autoclass:: spans.types.floatrange

String range
~~~~~~~~~~~~
.. autoclass:: spans.types.strrange

Date range
~~~~~~~~~~
.. autoclass:: spans.types.daterange
   :members:
   :special-members: __len__

Period range
~~~~~~~~~~~~
.. autoclass:: spans.types.PeriodRange
   :members:

Datetime range
~~~~~~~~~~~~~~
.. autoclass:: spans.types.datetimerange

Timedelta range
~~~~~~~~~~~~~~~
.. autoclass:: spans.types.timedeltarange


Range sets
----------

Range set
~~~~~~~~~
.. autoclass:: spans.settypes.rangeset
   :members:
   :special-members: __iter__, __len__

Discrete range set
~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.discreterangeset
   :members: values

Offsetable range set
~~~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.offsetablerangeset
   :members: offset

Integer range set
~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.intrangeset

Float range set
~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.floatrangeset

String range set
~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.strrangeset

Date range set
~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.daterangeset

Datetime range set
~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.datetimerangeset

Timedelta range set
~~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.timedeltarangeset
