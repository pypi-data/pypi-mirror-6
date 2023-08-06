"""
    tests.unit.optional_test
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import missing
from schemes.modifiers import Optional
from tests.unit import FakeField


def test_emits_value_according_to_field_rules():
    field = Optional(FakeField())
    assert field.emit(0) == u'emit(0)'


def test_coerces_none_to_none():
    field = Optional(FakeField())
    assert field.coerce(None) is None


def test_coerces_non_none_value_according_to_field_rules():
    field = Optional(FakeField())
    assert field.coerce(0) == u'coerce(0)'


def test_accepts_missing_value_as_none_on_create_if_no_default_is_set():
    field = Optional(FakeField())
    assert field._accept(missing, True) is None


def test_accepts_missing_value_as_default_value_on_create():
    field = Optional(FakeField(), default=u'default')
    assert field._accept(missing, True) == u'default'


def test_supports_callable_default_value():
    field = Optional(FakeField(), default=lambda: u'default')
    assert field._accept(missing, True) == u'default'


@pytest.mark.parametrize('creating', (True, False))
def test_accepts_none_value_if_default_is_none(creating):
    field = Optional(FakeField())
    assert field._accept(None, creating) is None


@pytest.mark.parametrize('creating', (True, False))
def test_accepts_other_values_according_to_field_rules(creating):
    field = Optional(FakeField())
    assert field._accept(0, creating) == u'accept(0, {})'.format(creating)


def test_forces_embedding_of_component_field():
    field = Optional(FakeField())
    assert field.element.has_been_embedded
