# -*- coding: utf-8 -*-

# $Id: test_config.py 904 2014-04-25 19:56:50Z alex $


import os
import tempfile
import unittest

from arv.autotest.config import ConfigurationError
from arv.autotest.config import _parse_config
from arv.autotest.config import read_config
from arv.autotest.utils import NoDefault



def is_int(value):
    if not isinstance(value, int):
        raise ValueError()
    return value


class TestParseConfig(unittest.TestCase):

    def setUp(self):
        self.SCHEMA = {
            "command" : (NoDefault, None),
            "verbosity": (0, is_int),
        }

    def test_parses_ok(self):
        config = """
        {
            "command" : "echo 1",
            "verbosity" : 2
        }
        """
        cfg = _parse_config(config, self.SCHEMA)
        self.assertEqual(cfg.command, "echo 1")
        self.assertEqual(cfg.verbosity, 2)

    def test_raises_ConfigurationError_if_wrong_option_name(self):
        config = """
        {
            "wrong" : "echo 1",
            "verbosity" : 2
        }
        """
        self.assertRaises(
            ConfigurationError,
            _parse_config, config, self.SCHEMA
        )

    def test_raises_ConfigurationError_if_wrong_option_value(self):
        config = """
        {
            "command" : "echo 1",
            "verbosity" : "2"
        }
        """
        self.assertRaises(
            ConfigurationError,
            _parse_config, config, self.SCHEMA
        )


class TestReadConfig(unittest.TestCase):

    def setUp(self):
        self.SCHEMA = {
            "command" : (NoDefault, None),
            "verbosity": (0, is_int),
        }

    def create_config_file(self, contents):
        handle, path = tempfile.mkstemp()
        os.write(handle, contents)
        os.close(handle)
        return path

    def test_raises_ConfigurationError_if_config_file_missing(self):
        path = "/i/hope/this/file/does/not/exists.cfg"
        self.failIf(os.path.isfile(path))
        self.assertRaises(
            ConfigurationError,
            read_config, path
        )

    def test_ok(self):
        config = b"""
        {
            "command" : "echo 1",
            "verbosity" : 2
        }
        """
        path = self.create_config_file(config)
        cfg = read_config(path, self.SCHEMA)
        self.assertEqual(cfg.command, "echo 1")
        self.assertEqual(cfg.verbosity, 2)
