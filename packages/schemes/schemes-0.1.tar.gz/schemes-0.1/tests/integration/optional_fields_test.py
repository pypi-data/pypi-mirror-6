"""
    tests.integration.optional_fields_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError


def test_creation_succeeds_with_missing_optional_fields(optional_schema):
    data = {'b': True}
    document = optional_schema.create(data)
    assert ((document['b'] is document.b is True) and
            (document['nested'] is document.nested is None) and
            (document['nullable'] is document.nullable is None) and
            (document['nonnullable'] == document.nonnullable == u''))


def test_creation_succeeds_with_allowed_explicit_none(optional_schema):
    data = {'b': True, 'nullable': None}
    document = optional_schema.create(data)
    assert ((document['b'] is document.b is True) and
            (document['nested'] is document.nested is None) and
            (document['nullable'] is document.nullable is None) and
            (document['nonnullable'] == document.nonnullable == u''))


def test_creation_fails_with_disallowed_explicit_none(optional_schema):
    data = {'b': True, 'nonnullable': None}
    with pytest.raises(ValidationError) as info:
        optional_schema.create(data)
    assert info.value.reason == {'nonnullable': u"Field cannot be null."}


def test_patch_succeeds_with_missing_optional_fields(optional_schema):
    embedded = {'b': False, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = optional_schema.coerce({'b': False, 'nullable': 42L,
                                       'nonnullable': u"Hello",
                                       'nested': embedded})
    data = {'b': True}
    document = optional_schema.patch(document, data)
    assert ((document['b'] is document.b is True) and
            (document['nested'] == document.nested == embedded) and
            (document['nullable'] == document.nullable == 42L) and
            (document['nonnullable'] == document.nonnullable == u"Hello"))


def test_patch_fails_with_disallowed_explicit_none(optional_schema):
    embedded = {'b': False, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = {'b': False, 'nullable': 42L, 'nonnullable': u"Hello",
                'nested': embedded}
    data = {'b': True, 'nonnullable': None}
    with pytest.raises(ValidationError) as info:
        optional_schema.patch(document, data)
    assert info.value.reason == {'nonnullable': u"Field cannot be null."}


def test_patch_fails_with_missing_fields_in_optional_embedded(optional_schema):
    embedded = {'b': False, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = {'b': False, 'nullable': 42L, 'nonnullable': u"Hello",
                'nested': embedded}
    data = {'b': True, 'nested': {'b': True, 'f': 42.42, 'l': 42L}}
    with pytest.raises(ValidationError) as info:
        optional_schema.patch(document, data)
    assert info.value.reason == {'nested': {'i': u"Field is missing.",
                                            's': u"Field is missing."}}
