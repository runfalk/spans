.. module:: spans

API documentation
=================
This is the API reference for all public classes and functions in Spans.


Ranges
------

Range class
~~~~~~~~~~~
.. autoclass:: spans.types.Range
   :members:


Discrete range
~~~~~~~~~~~~~~
.. autoclass:: spans.types.DiscreteRange
   :members:


Offsetable range mixin
~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.types.OffsetableRangeMixin
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
.. autoclass:: spans.settypes.RangeSet
   :members:
   :special-members: __iter__, __len__


Discrete range set mixin
~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.DiscreteRangeSetMixin
   :members: values


Offsetable range set mixin
~~~~~~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.OffsetableRangeSetMixin
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


Meta range set
~~~~~~~~~~~~~~
.. autoclass:: spans.settypes.MetaRangeSet



Legacy names
------------
Historically some internal Spans classes had all lowercase names. This was changed in version 0.5.0. The reason some classes still have lowercase names is to match the Python built-ins they map to. ``date``'s range type is and will always be :class:`~spans.types.daterange`. However, it doesn't make much sense to maintain this convention for the more hidden classes in Spans.

.. automodule:: spans.types
   :members: range_, discreterange, offsetablerange

.. automodule:: spans.settypes
   :members: metarangeset, rangeset
