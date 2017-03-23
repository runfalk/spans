from timeit import timeit, repeat

from spans import *


def format_sec(s):
    """
    Format seconds in a more human readable way. It supports units down to
    nanoseconds.

    :param s: Float of seconds to format
    :return: String second representation, like 12.4 us
    """

    prefixes = ["", "m", "u", "n"]
    unit = 0

    while s < 1 and unit + 1 < len(prefixes):
        s *= 1000
        unit += 1

    return "{:.1f} {}s".format(s, prefixes[unit])


def run_benchmark(func, number=None):
    if number is None:
        number = 1000

    total_time = sum(repeat(func, repeat=3, number=number)) / 3

    print("{func:.<40} {loops} loops, best of 3: {per_loop} per loop".format(
        func=func.__name__ + " ",
        loops=number,
        per_loop=format_sec(total_time / float(number))))


# Create ranges here to prevent __init__ from affecting test results
a = intrange(1, 5)
b = intrange(5, 10)
c = intrange(10, 15)

ab = a.union(b)
bc = b.union(c)

abc = ab.union(c)


def test_union():
    a.union(b)
    ab.union(bc)


def test_intersection():
    a.intersection(b)
    ab.intersection(bc)


def test_difference():
    a.difference(b)
    ab.difference(bc)


def test_overlap():
    a.overlap(b)
    ab.overlap(bc)


def test_left_of():
    a.left_of(bc)
    b.left_of(a)


tests = [func for name, func in locals().items() if name.startswith("test_")]
for func in sorted(tests, key=lambda v: v.__name__):
    run_benchmark(func, number=10000)
