# -*- coding: utf-8 -*-

# $Id: validators.py 904 2014-04-25 19:56:50Z alex $

"""Module defining validators and validator factories.

A validator is any callable that receives a value and performs some
test on it. If the validation succeeds the validator must return a
value, either the original value or the result of some
computation/conversion. If the check fails it raises a ``ValueError``
exception.

"""

import os.path
import re

import six

from arv.autotest.utils import TypedObject


def make_validator_from_predicate(predicate):
    """Returns a validator that succeeds if the value it receives holds
    true according to the predicate. The return value of the validator
    is the original value.

    The predicate should be a callable that receives a value and
    returns a boolean, ``True`` if the predicate holds true, ``False``
    otherwise.

    """
    def validator(value):
        if not predicate(value):
            raise ValueError(value)
        return value
    return validator

def make_validator_from_class(class_):
    """Returns a validator that succedds if the value it receives is an
    instance of the given class. The return value of the validator is
    the original value.

    """
    def validator(value):
        if not isinstance(value, class_):
            raise ValueError(value)
        return value
    return validator

def make_validator_from_schema(schema):
    """Returns a validator that succeeds it the dictionary it receives is
    compliant with the schema. The return value of the validator is an
    instance of the :py:class:`~arv.autotest.utils.TypedObject` class.

    """
    def validator(value):
        o = TypedObject(schema)
        for k, v in value.items():
            try:
                setattr(o, k, v)
            except AttributeError:
                # comment required to circunvent a bug in coverage
                raise ValueError(value)
        return o
    return validator

def compose(*functions):
    """Returns a validator built composing the validators it receives as
    arguments::

      compose(v1, v2)(value) === v2(v1(value))

    It succeeds if all validators succeed. The return value of the
    validator is the value returned by the last validator.

    """
    def validator(value):
        for f in functions:
            value = f(value)
        return value
    return validator

def all(*validators):
    """Returns a validator that applies each validator in turn to the
    value it receives.

    It succeeds if all validators succeed. The intermediate values
    returned by the validators is ignored. The return value is the
    original value.

    """
    def validator(value):
        for v in validators:
            v(value)
        return value
    return validator

def is_list_of(item_validator):
    """Returns a validator for iterables that succeeds if the validator
    ``item_validator`` succeeds on all the items in the iterable.

    The validator returns a list containing the result of validating
    each item in the iterable.

    """
    def validator(value):
        return [item_validator(i) for i in value]
    return validator

is_bool = make_validator_from_class(bool)
is_dir = make_validator_from_predicate(os.path.isdir)
is_float = make_validator_from_class(float)
is_int = make_validator_from_class(int)
is_str = make_validator_from_class(six.binary_type)
is_unicode = make_validator_from_class(six.text_type)

is_regex = compose(
    is_unicode,
    lambda x: re.compile(x + "$")
)
