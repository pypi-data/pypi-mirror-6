"""
    tests.unit.writeonly_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import SkipElement
from schemes.modifiers import WriteOnly, Internal
from tests.unit import FakeField


@pytest.mark.parametrize('modifier', (WriteOnly, Internal))
def test_skips_value_on_emit(modifier):
    field = modifier(FakeField())
    with pytest.raises(SkipElement):
        field.emit(0)


@pytest.mark.parametrize('modifier', (WriteOnly, Internal))
def test_coerces_value_according_to_field_rules(modifier):
    field = modifier(FakeField())
    assert field.coerce(0) == u'coerce(0)'


@pytest.mark.parametrize('creating', (True, False))
def test_accepts_values_according_to_field_rules(creating):
    field = WriteOnly(FakeField())
    assert field._accept(0, creating) == u'accept(0, {})'.format(creating)


def test_forces_embedding_of_component_field():
    field = WriteOnly(FakeField())
    assert field.element.has_been_embedded
