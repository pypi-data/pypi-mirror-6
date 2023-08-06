# -*- coding: utf-8 -*-

# $Id: test_typed_object.py 904 2014-04-25 19:56:50Z alex $


import unittest

from arv.autotest.config import NoDefault
from arv.autotest.config import TypedObject

def is_int(value):
    if not isinstance(value, int):
        raise ValueError()
    return value

class TestSetAttr(unittest.TestCase):

    def setUp(self):
        self.options = {
            "verbosity": (0, is_int),
            "whatever": (None, None),
            "doubled": (0, lambda x : is_int(x) * 2)
        }
        self.typed_object = TypedObject(self.options)

    def test_ok_if_name_exists_and_validator_passes(self):
        name = "verbosity"
        value = 2
        self.assert_(name in self.typed_object._values)
        self.assert_(callable(self.typed_object._validators[name]))
        setattr(self.typed_object, name, value)
        self.assertEqual(getattr(self.typed_object, name), value)

    def test_ok_if_name_exists_and_validator_is_not_callable(self):
        name = "whatever"
        self.assert_(name in self.typed_object._values)
        self.failIf(callable(self.typed_object._validators[name]))
        setattr(self.typed_object, name, 123)
        setattr(self.typed_object, name, "xyz")

    def test_raises_AttributeError_if_wrong_name(self):
        name = "missing"
        self.failIf(name in self.typed_object._values)
        self.assertRaises(
            AttributeError,
            self.typed_object.__setattr__, name, "xyz"
        )

    def test_raises_ValueError_if_validator_fails(self):
        name = "verbosity"
        value = "2"
        self.assertRaises(
            ValueError,
            self.typed_object._validators[name], value
        )
        self.assertRaises(
            ValueError,
            self.typed_object.__setattr__, name, value
        )

    def test_validator_may_alter_assigned_value(self):
        self.typed_object.doubled = 1
        self.assertEqual(self.typed_object.doubled, 2)

    def test_ensure__dict__is_not_modified(self):
        self.typed_object.verbosity = 2
        self.failIf("verbosity" in self.typed_object.__dict__)


class TestGetAttr(unittest.TestCase):

    def setUp(self):
        self.options = {
            "command": (NoDefault, str),
            "verbosity": (0, is_int),
        }
        self.typed_object = TypedObject(self.options)

    def test_raises_AttributeError_if_name_does_not_exists(self):
        name = "missing"
        self.failIf(name in self.typed_object._values)
        self.assertRaises(
            AttributeError,
            getattr, self.typed_object, name
        )

    def test_raises_AttributeError_if_name_exists_but_has_no_value_and_no_default(self):
        name = "command"
        self.assert_(self.typed_object._values[name] is NoDefault)
        self.assertRaises(
            AttributeError,
            getattr, self.typed_object, name
        )

    def test_ok_if_name_exists_and_has_default(self):
        name = "verbosity"
        self.failIf(self.typed_object._values[name] is NoDefault)
        self.assertEqual(getattr(self.typed_object, name), 0)

    def test_ok_if_name_exists_and_has_value(self):
        name = "verbosity"
        setattr(self.typed_object, name, 123)
        self.assertEqual(getattr(self.typed_object, name), 123)
