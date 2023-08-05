from unittest import TestCase

from nose.tools import eq_

from elasticutils.utils import chunked


class ChunkedTests(TestCase):
    def test_chunked(self):
        # chunking nothing yields nothing.
        eq_(list(chunked([], 1)), [])

        # chunking list where len(list) < n
        eq_(list(chunked([1], 10)), [(1,)])

        # chunking a list where len(list) == n
        eq_(list(chunked([1, 2], 2)), [(1, 2)])

        # chunking list where len(list) > n
        eq_(list(chunked([1, 2, 3, 4, 5], 2)),
            [(1, 2), (3, 4), (5,)])
