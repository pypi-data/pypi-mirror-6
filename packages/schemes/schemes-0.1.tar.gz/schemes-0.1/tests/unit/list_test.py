"""
    tests.unit.list_test
    ~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError
from schemes.fields import List
from tests.unit import FakeField


def test_emits_values_according_to_its_component():
    field = List(FakeField())
    assert field.emit([0, 1]) == [u'emit(0)', u'emit(1)']


def test_coerces_a_list_of_values_according_to_its_component():
    field = List(FakeField())
    assert field.coerce([0, 1]) == [u'coerce(0)', u'coerce(1)']


@pytest.mark.parametrize('creating', (True, False))
def test_accepts_a_list_of_values_according_to_its_component(creating):
    field = List(FakeField())
    assert field._accept([0, 1], creating) == [
        u'accept(0, {})'.format(creating),
        u'accept(1, {})'.format(creating)]


@pytest.mark.parametrize('creating', (True, False))
def test_rejects_a_list_containing_unacceptable_values(creating):
    field = List(FakeField())
    with pytest.raises(ValidationError) as info:
        field._accept([0, ValidationError(u"Item 1.")], creating)
    assert info.value.reason == {1: u"Item 1."}


@pytest.mark.parametrize('creating', (True, False))
def test_reports_multiple_validation_errors(creating):
    field = List(FakeField())
    with pytest.raises(ValidationError) as info:
        field._accept(
            [ValidationError(u"Item 0."), ValidationError(u"Item 1."), 2],
            creating)
    assert info.value.reason == {0: u"Item 0.",
                                 1: u"Item 1."}


def test_forces_embedding_of_component_field():
    field = List(FakeField())
    assert field.element.has_been_embedded
