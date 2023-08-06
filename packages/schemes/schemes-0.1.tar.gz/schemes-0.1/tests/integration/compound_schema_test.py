"""
    tests.integration.compound_schema_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError
from schemes.utils import AttrDict


def test_coercion_upgrades_recursively(nested_schema):
    data = {'d': {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}}
    document = nested_schema.coerce(data)
    embedded_document = document.d
    assert ((embedded_document['b'] is embedded_document.b is True) and
            (embedded_document['i'] == embedded_document.i == 42) and
            (embedded_document['f'] == embedded_document.f == 42.42) and
            (embedded_document['l'] == embedded_document.l == 42L) and
            (embedded_document['s'] == embedded_document.s == u'Hello'))


def test_creation_succeeds_with_complete_correct_fields(nested_schema):
    data = {'d': {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}}
    document = nested_schema.create(data)
    embedded_document = document.d
    assert ((embedded_document['b'] is embedded_document.b is True) and
            (embedded_document['i'] == embedded_document.i == 42) and
            (embedded_document['f'] == embedded_document.f == 42.42) and
            (embedded_document['l'] == embedded_document.l == 42L) and
            (embedded_document['s'] == embedded_document.s == u'Hello'))


def test_creation_fails_with_missing_correct_fields(nested_schema):
    data = {'d': {'b': True, 'f': 42.42, 'l': 42L}}
    with pytest.raises(ValidationError) as info:
        nested_schema.create(data)
    assert info.value.reason == {'d': {'i': u"Field is missing.",
                                       's': u"Field is missing."}}


def test_patch_succeeds_with_complete_correct_fields(nested_schema):
    document = nested_schema.coerce(
        {'d': {'b': False, 'i': 0, 'f': 0.0, 'l': 0L, 's': u''}})
    data = {'d': {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}}
    document = nested_schema.patch(document, data)
    embedded_document = document.d
    assert ((embedded_document['b'] is embedded_document.b is True) and
            (embedded_document['i'] == embedded_document.i == 42) and
            (embedded_document['f'] == embedded_document.f == 42.42) and
            (embedded_document['l'] == embedded_document.l == 42L) and
            (embedded_document['s'] == embedded_document.s == u'Hello'))


def test_patch_succeeds_with_omitted_embedded_document(nested_schema):
    document = nested_schema.coerce(
        {'d': {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}})
    document = nested_schema.patch(document, {})
    embedded_document = document.d
    assert ((embedded_document['b'] is embedded_document.b is True) and
            (embedded_document['i'] == embedded_document.i == 42) and
            (embedded_document['f'] == embedded_document.f == 42.42) and
            (embedded_document['l'] == embedded_document.l == 42L) and
            (embedded_document['s'] == embedded_document.s == u'Hello'))


def test_patch_fails_with_missing_correct_fields(nested_schema):
    document = nested_schema.coerce(
        {'d': {'b': False, 'i': 0, 'f': 0.0, 'l': 0L, 's': u''}})
    data = {'d': {'b': True, 'f': 42.42, 'l': 42L}}
    with pytest.raises(ValidationError) as info:
        nested_schema.patch(document, data)
    assert info.value.reason == {'d': {'i': u"Field is missing.",
                                       's': u"Field is missing."}}
