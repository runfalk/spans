.. doctest::

    >>> from spans import daterange
    >>> from datetime import date
    >>> the90s = daterange(date(1990, 1, 1), date(2000, 1, 1))
    >>> date(1996, 12, 4) in the90s
    True
    >>> date(2000, 1, 1) in the90s
    False
    >>> the90s.union(daterange(date(2000, 1, 1), date(2010, 1, 1)))
    daterange([datetime.date(1990, 1, 1),datetime.date(2010, 1, 1)))
