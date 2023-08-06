# -*- coding: utf-8 -*-

# $Id: test_runner.py 904 2014-04-25 19:56:50Z alex $


import unittest

from arv.autotest.runner import run


class TestRunner(unittest.TestCase):

    def setUp(self):
        class R(object):
            def __init__(self):
                self.input = []
                self.code = None
            def start(self):
                pass
            def feed(self, data):
                self.input.append(data)
            def stop(self, code):
                self.code = code
        self.reactor = R()

    def test_exit_code_0(self):
        run("echo 'hello' && exit 0", self.reactor)
        self.assertEqual(self.reactor.code, 0)
        self.assertEqual(b"".join(self.reactor.input), b"hello\n")

    def test_exit_code_1(self):
        run("echo 'hello' && exit 1", self.reactor)
        self.assertEqual(self.reactor.code, 1)
        self.assertEqual(b"".join(self.reactor.input), b"hello\n")

