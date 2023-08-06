import sys as _sys
import argparse as _argparse
import unittest as _unittest
import collections as _collections
import pprint as _pprint
import math as _math
import functools as _functools
import operator as _operator
import multiprocessing as _multiprocessing
import itertools as _itertools


__version__ = '0.0.13'


class Error(Exception):
    pass


TICK_INTERVAL_PADDING_RATIO = 0.1


def each_cons(xs, n):
    assert n >= 1
    return [xs[i:i+n] for i in range(len(xs) - (n - 1))]


def parallel_for(f, *indicess):
    return reshape(_multiprocessing.Pool().starmap(f, _itertools.product(*indicess)),
                   [len(indices) for indices in indicess])


def reshape(xs, ns):
    assert ns
    assert len(xs) == _functools.reduce(_operator.mul, ns, 1)
    return _reshape(xs, ns)


def _reshape(xs, ns):
    if len(ns) == 1:
        return xs
    return _reshape(partition(xs, ns[-1]), ns[0:-1])


def partition(xs, n):
    ret = []
    for i in range(n, len(xs) + 1, n):
        ret.append(xs[i - n:i])
    return ret


def memoize(f):
    cache = {}
    def memoized_f(*args):
        if args in cache:
            return cache[args]
        else:
            cache[args] = retv = f(*args)
            return retv
    memoized_f.cache = cache
    return memoized_f


def profiled_memoize(f):
    cache = {}
    profile = {'new': 0,
               'hit': 0}
    def profiled_memoized_f(*args):
        if args in cache:
            profile['hit'] += 1
            return cache[args]
        else:
            profile['new'] += 1
            cache[args] = retv = f(*args)
            return retv
    profiled_memoized_f.cache = cache
    profiled_memoized_f.profile = profile
    return profiled_memoized_f


def _get_interval(lx):
    assert lx > 0
    dx = 10**(_math.ceil(_math.log10(lx)) - 1)
    if lx > 5*dx:
        return dx
    elif lx > 2*dx:
        return 5*dx/10
    else:
        return 2*dx/10


def _get_lower_limit(x, dx,
                     padding_ratio=TICK_INTERVAL_PADDING_RATIO):
    assert dx > 0
    lower = _math.floor(x/dx)*dx
    if x <= lower + dx*padding_ratio:
        lower -= dx
    return lower


def _get_upper_limit(x, dx,
                     padding_ratio=TICK_INTERVAL_PADDING_RATIO):
    assert dx > 0
    upper = _math.ceil(x/dx)*dx
    if x >= upper - dx*padding_ratio:
        upper += dx
    return upper


def get_tick_configurations(x1, x2,
                            padding_ratio=TICK_INTERVAL_PADDING_RATIO):
    x_small, x_large = sorted([x1, x2])
    dx = _get_interval(x_large - x_small)
    lower = _get_lower_limit(x_small, dx, padding_ratio)
    upper = _get_upper_limit(x_large, dx, padding_ratio)
    return lower, upper, dx


def pp(x):
    _pprint.pprint(x, stream=_sys.stderr)
    return x


def flatten(xss):
    """
    # Flatten containers

    ## Note
    Do not include recursive elements.

    ## Exceptions
    - `RuntimeError`: Recursive elements will cause this
    """
    if isinstance(xss, str):
        yield xss
    else:
        for xs in xss:
            if isinstance(xs, _collections.Iterable):
                for x in flatten(xs):
                    yield x
            else:
                yield xs


def list_2d(n_row, n_column, init=None):
    assert n_row >= 1
    assert n_column >= 1

    return [[init
             for _
             in range(n_column)]
            for _
            in range(n_row)]


def make_fixed_format_parser(fields):
    """
    fields: (('density', 3, int),
             ('opacity', 7, float))
    """
    lower = 0
    _fields = []
    for field in fields:
        if len(field) != 3:
            exit('len(field) != 3 {}'.format(field))
        name, length, converter = field
        assert length >= 1
        upper = lower + length
        _field = (name, lower, upper, converter)
        lower = upper
        _fields.append(_field)

    def fixed_format_parser(s):
        assert len(s) >= upper
        return {name: converter(s[lower:upper])
                for name, lower, upper, converter
                in _fields}
    return fixed_format_parser


class TestAction(_argparse.Action):
    def __init__(self,
                 option_strings,
                 dest=_argparse.SUPPRESS,
                 default=_argparse.SUPPRESS,
                 help=None):
        super().__init__(option_strings=option_strings,
                         dest=dest,
                         default=default,
                         nargs=0,
                         help=help)


    def __call__(self, parser, namespace, values, option_string=None):
        _unittest.main(argv=_sys.argv[:1])
        parser.exit()


def _fn_for_test_parallel_for(x, y):
    return x, y


class _Tester(_unittest.TestCase):

    def test_each_cons(self):
        with self.assertRaises(AssertionError):
            each_cons([1, 2, 3], 0)

        for xs, n, expected in (
                ([], 1, [],),
                ([1, 2, 3], 1, [[1], [2], [3]],),
                ([1, 2, 3], 2, [[1, 2], [2, 3]],),
                ([1, 2, 3], 3, [[1, 2, 3]],),
                ([1, 2, 3], 4, [],),
        ):
            self.assertEqual(each_cons(xs, n), expected)

    def test_parallel_for(self):
        self.assertEqual(parallel_for(_fn_for_test_parallel_for, [1, 2], [3, 4, 5]), [[(1, 3), (1, 4), (1, 5)], [(2, 3), (2, 4), (2, 5)]])

    def test_reshape(self):
        with self.assertRaises(AssertionError):
            reshape((1,), ())
        with self.assertRaises(AssertionError):
            reshape((1, 2, 3), (2, 2))

        for xs, ns, expected in (
                ([1, 2, 3], (3,), [1, 2, 3]),
                ([1, 2, 3], (3, 1), [[1], [2], [3]]),
                ([1, 2, 3, 4], (2, 2), [[1, 2], [3, 4]]),
                ([1, 2, 3, 4, 5, 6], (2, 3), [[1, 2, 3], [4, 5, 6]]),
                ([1, 2, 3, 4, 5, 6, 7, 8], (2, 2, 2), [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]),
        ):
            self.assertEqual(reshape(xs, ns), expected)

    def test_partition(self):
        with self.assertRaises(ValueError):
            partition((1, 2), 0)

        for xs, n, expected in (
                ((), -1, []),
                ((1, 2), -1, []),

                ((), 1, []),
                ((), 2, []),

                ([1, 3], 1, [[1], [3]]),
                ([1, 4], 2, [[1, 4]]),
                ([1, 5], 3, []),
        ):
            self.assertEqual(partition(xs, n), expected)

    def test__get_interval(self):
        with self.assertRaises(AssertionError):
            _get_interval(-1)
        with self.assertRaises(AssertionError):
            _get_interval(0)

        lx_dx = [(1, 0.1),

                 (2, 0.2),

                 (3, 0.5),
                 (4, 0.5),
                 (5, 0.5),

                 (6, 1),
                 (7, 1),
                 (8, 1),
                 (9, 1),
                 (10, 1),

                 (11, 2),
                 (12, 2),
                 (19, 2),
                 (20, 2),

                 (21, 5),
                 (22, 5),
                 (49, 5),
                 (50, 5),

                 (51, 10),
                 (52, 10),
                 (99, 10),
                 (100, 10)]
        for lx, dx in lx_dx:
            self.assertAlmostEqual(_get_interval(lx), dx)

    def test__get_lower_limit(self):
        with self.assertRaises(AssertionError):
            _get_lower_limit(0, 0)
        with self.assertRaises(AssertionError):
            _get_lower_limit(0, -1)

        self.assertAlmostEqual(_get_lower_limit(-10, 3), -12)
        self.assertAlmostEqual(_get_lower_limit(-12, 3), -15)

    def test__get_upper_limit(self):
        with self.assertRaises(AssertionError):
            _get_upper_limit(0, 0)
        with self.assertRaises(AssertionError):
            _get_upper_limit(0, -1)

        self.assertAlmostEqual(_get_upper_limit(-10, 3), -9)
        self.assertAlmostEqual(_get_upper_limit(-12, 3), -9)

    def test_get_tick_configurations(self):
        x1, x2, dx = get_tick_configurations(101.001, 103.0001)
        self.assertAlmostEqual(x1, 100.8)
        self.assertAlmostEqual(x2, 103.2)
        self.assertAlmostEqual(dx, 0.2)

        x1, x2, dx = get_tick_configurations(0, 1)
        self.assertAlmostEqual(x1, -0.1)
        self.assertAlmostEqual(x2, 1.1)
        self.assertAlmostEqual(dx, 0.1)

    def test_list_2d(self):
        self.assertEqual(list_2d(2, 3),
                         [[None, None, None],
                          [None, None, None]])

        self.assertEqual(list_2d(2, 3, 0),
                         [[0, 0, 0],
                          [0, 0, 0]])

    def test_flatten(self):
        self.assertEqual(list(flatten([])), [])
        self.assertEqual(list(flatten([1, 2])), [1, 2])
        self.assertEqual(list(flatten([1, [2, 3]])), [1, 2, 3])
        self.assertEqual(list(flatten(['ab'])), ['ab'])
        self.assertEqual(tuple(sorted(flatten((1, 2, (3, [4, set([5, 6]), 7 ], [8, 9]))))),
                         tuple(sorted((1, 2, 3, 4, 5, 6, 7, 8, 9))))

    def test_make_fixed_format_parser(self):
        with self.assertRaises(AssertionError):
            make_fixed_format_parser((('a', 0, int),))
        fixed_format_parser\
            = make_fixed_format_parser((('a', 3, int),
                                        ('b', 7, lambda x: -int(x))))
        self.assertEqual(fixed_format_parser(' 325      '),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser(' 325      \n'),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser(' 32  5    '),
                         {'a': 32, 'b': -5})
        self.assertEqual(fixed_format_parser('32   5    abc'),
                         {'a': 32, 'b': -5})
        with self.assertRaises(AssertionError):
            fixed_format_parser('123456789')


if __name__ == '__main__':
    _unittest.main()
