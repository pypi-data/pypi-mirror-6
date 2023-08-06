# -*- coding: utf-8 -*-

# $Id: test_memoize.py 904 2014-04-25 19:56:50Z alex $


import unittest

from arv.autotest.utils import memoize


class TestMemoize(unittest.TestCase):

    def setUp(self):
        class Foo(object):
            def __init__(self, seed=0):
                self.call_counter = seed
            def method(self, a):
                self.call_counter += 1
                return a + self.call_counter
            @memoize
            def memoized(self, a):
                return self.method(a)
        self.foo = Foo(seed=0)
        self.bar = Foo(seed=100)

    def test_preconditions(self):
        self.assertEqual(self.foo.call_counter, 0)
        self.assertEqual(self.foo.method(3), 4)
        self.assertEqual(self.foo.call_counter, 1)
        self.assertEqual(self.foo.method(3), 5)
        self.assertEqual(self.foo.call_counter, 2)
        self.assertEqual(self.bar.call_counter, 100)
        self.assertEqual(self.bar.method(3), 104)
        self.assertEqual(self.bar.call_counter, 101)
        self.assertEqual(self.bar.method(3), 105)
        self.assertEqual(self.bar.call_counter, 102)

    def test_memoize_avoids_repeated_calls(self):
        self.assertEqual(self.foo.call_counter, 0)
        self.assertEqual(self.foo.memoized(3), 4)
        self.assertEqual(self.foo.call_counter, 1)
        self.assertEqual(self.foo.memoized(3), 4)
        self.assertEqual(self.foo.call_counter, 1)

    def test_memoize_performs_different_repeated_calls(self):
        self.assertEqual(self.foo.call_counter, 0)
        self.assertEqual(self.foo.memoized(3), 4)
        self.assertEqual(self.foo.call_counter, 1)
        self.assertEqual(self.foo.memoized(4), 6)
        self.assertEqual(self.foo.call_counter, 2)

    def test_memoize_cache_isolates_instances(self):
        self.assertEqual(self.foo.memoized(3), 4)
        self.assertEqual(self.bar.memoized(3), 104)
