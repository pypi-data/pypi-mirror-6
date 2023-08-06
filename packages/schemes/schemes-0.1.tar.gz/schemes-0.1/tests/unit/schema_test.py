"""
    tests.unit.schema_test
    ~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError, SkipElement
from schemes.schema import Schema
from schemes.utils import AttrDict
from tests.unit import FakeField


@pytest.fixture(scope='session')
def definition():
    return {'a': FakeField(), 'b': FakeField(), 'c': FakeField()}


@pytest.fixture
def schema(definition):
    return Schema(definition)


@pytest.fixture(params=(False, True))
def field(request, schema):
    return schema.embedded if request.param else schema


def test_emits_values_according_to_its_definition(field):
    value = {'a': 0, 'b': 1, 'c': 2}
    assert field.emit(value) == {'a': u'emit(0)',
                                 'b': u'emit(1)',
                                 'c': u'emit(2)'}


def test_filters_out_undefined_fields_when_emitting(field):
    value = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4}
    assert field.emit(value) == {'a': u'emit(0)',
                                 'b': u'emit(1)',
                                 'c': u'emit(2)'}


def test_filters_out_skippable_fields_when_emitting(field):
    value = {'a': 0, 'b': SkipElement(), 'c': 2}
    assert field.emit(value) == {'a': u'emit(0)', 'c': u'emit(2)'}


def test_coerces_a_dictionary_according_to_its_definitions(schema):
    value = {'a': 0, 'b': 1, 'c': 2}
    assert schema.coerce(value) == {'a': u'coerce(0)',
                                    'b': u'coerce(1)',
                                    'c': u'coerce(2)'}


def test_coerces_to_document_type(field):
    value = {'a': 0, 'b': 1, 'c': 2}
    assert isinstance(field.coerce(value), field.document_type)


@pytest.mark.parametrize('creating', (True, False))
def test_accepts_a_dictionary_according_to_its_definition(schema, creating):
    value = {'a': 0, 'b': 1, 'c': 2}
    assert schema._accept(value, creating) == {
        'a': u'accept(0, {})'.format(creating),
        'b': u'accept(1, {})'.format(creating),
        'c': u'accept(2, {})'.format(creating)}


@pytest.mark.parametrize('creating', (True, False))
def test_forces_creating_on_accept_when_embedded(schema, creating):
    value = {'a': 0, 'b': 1, 'c': 2}
    assert schema.embedded._accept(value, creating) == {
        'a': u'accept(0, True)',
        'b': u'accept(1, True)',
        'c': u'accept(2, True)'}


@pytest.mark.parametrize('creating', (True, False))
def test_creates_an_attrdict_by_default_on_accept(field, creating):
    value = {'a': 0, 'b': 1, 'c': 2}
    assert isinstance(field._accept(value, creating), AttrDict)


@pytest.mark.parametrize('creating', (True, False))
def test_creates_a_custom_dict_on_demand(creating):
    class MyDict(dict):
        pass
    field = Schema({'a': FakeField()}, document_type=MyDict)
    assert isinstance(field._accept({'a': 0}, creating), MyDict)


@pytest.mark.parametrize('creating', (True, False))
def test_filters_out_skippable_elements_when_accepting(field, creating):
    value = {'a': 0, 'b': SkipElement(), 'c': 2}
    assert 'b' not in field._accept(value, creating)


@pytest.mark.parametrize('creating', (True, False))
def test_rejects_a_dictionary_containing_unacceptable_values(field, creating):
    value = {'a': 0, 'b': 1, 'c': ValidationError(u"Item c.")}
    with pytest.raises(ValidationError) as info:
        field._accept(value, creating)
    assert info.value.reason == {'c': u"Item c."}


@pytest.mark.parametrize('creating', (True, False))
def test_rejects_a_dictionary_containing_unknown_fields(field, creating):
    value = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
    with pytest.raises(ValidationError) as info:
        field._accept(value, creating)
    assert info.value.reason == {'d': u"Unexpected field."}


@pytest.mark.parametrize('creating', (True, False))
def test_reports_multiple_validation_errors(field, creating):
    value = {'a': ValidationError(u"Item a."),
             'b': 1,
             'c': ValidationError(u"Item c.")}
    with pytest.raises(ValidationError) as info:
        field._accept(value, creating)
    assert info.value.reason == {'a': u"Item a.", 'c': u"Item c."}


def test_supports_creation(schema):
    assert (schema.create({'a': 0, 'b': 1, 'c': 2}) ==
            schema._accept({'a': 0, 'b': 1, 'c': 2}, True))


def test_supports_patching(schema):
    document = {'a': 0, 'b': 1, 'c': 2}
    assert (schema.patch(document, {'a': 3, 'b': SkipElement(), 'c': 4}) ==
            {'a': u'accept(3, False)', 'b': 1, 'c': u'accept(4, False)'})


def test_exposes_field_definitions(schema, definition):
    assert (schema.fields.a is definition['a'] and
            schema.fields.b is definition['b'] and
            schema.fields.c is definition['c'])


def test_forces_embedding_of_component_fields(schema):
    assert all(each.has_been_embedded for _, each in schema.fields)
