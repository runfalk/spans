"""This module provides one dimensional continuous set support for python.

Python has a wonderful set class, it does however not handle continuous sets
between two endpoints. This module tries to mitigate that. The ranges' behavoir
are modeled after PostgresSQL 9.2's range types. Deviating from PostgresSQL's
behavoir is considered a bug.

In addition to the range types there are range sets. A range set is can be viewed
as a mutable list of ranges. A set enables discontinious chunks to be grouped
together.

"""

__version__ = "0.4.1"
__all__ = [
	"intrange",
	"floatrange",
	"strrange",
	"daterange",
	"datetimerange",
	"timedeltarange",

	"intrangeset",
	"floatrangeset",
	"strrangeset",
	"daterangeset",
	"datetimerangeset",
	"timedeltarangeset"
]

from .types import *
from .settypes import *
