"""
    tests.integration.basic_simple_schema_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError


def test_coercion_upgrades_to_document(simple_schema):
    data = {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = simple_schema.coerce(data)
    assert ((document['b'] is document.b is True) and
            (document['i'] == document.i == 42) and
            (document['f'] == document.f == 42.42) and
            (document['l'] == document.l == 42L) and
            (document['s'] == document.s == u'Hello'))


def test_creation_succeeds_with_complete_correct_fields(simple_schema):
    data = {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = simple_schema.create(data)
    assert ((document['b'] is document.b is True) and
            (document['i'] == document.i == 42) and
            (document['f'] == document.f == 42.42) and
            (document['l'] == document.l == 42L) and
            (document['s'] == document.s == u'Hello'))


def test_creation_fails_with_missing_correct_fields(simple_schema):
    data = {'b': True, 'f': 42.42, 'l': 42L}
    with pytest.raises(ValidationError) as info:
        simple_schema.create(data)
    assert info.value.reason == {'i': u"Field is missing.",
                                 's': u"Field is missing."}


def test_creation_fails_with_incorrect_fields(simple_schema):
    data = {'b': True, 'i': u"0", 'f': 42.42, 'l': 42L, 's': 0}
    with pytest.raises(ValidationError) as info:
        simple_schema.create(data)
    assert info.value.reason == {'i': u"Wrong type. Must be int.",
                                 's': u"Wrong type. Must be string."}


def test_patch_succeeds_with_complete_correct_fields(simple_schema):
    document = simple_schema.coerce(
        {'b': False, 'i': 0, 'f': 0.0, 'l': 0L, 's': u''})
    data = {'b': True, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = simple_schema.patch(document, data)
    assert ((document['b'] is document.b is True) and
            (document['i'] == document.i == 42) and
            (document['f'] == document.f == 42.42) and
            (document['l'] == document.l == 42L) and
            (document['s'] == document.s == u'Hello'))


def test_patch_succeeds_with_missing_correct_fields(simple_schema):
    document = simple_schema.coerce(
        {'b': False, 'i': 42, 'f': 0.0, 'l': 0L, 's': u'Hello'})
    data = {'b': True, 'f': 42.42, 'l': 42L}
    document = simple_schema.patch(document, data)
    assert ((document['b'] is document.b is True) and
            (document['i'] == document.i == 42) and
            (document['f'] == document.f == 42.42) and
            (document['l'] == document.l == 42L) and
            (document['s'] == document.s == u'Hello'))


def test_patch_fails_with_incorrect_fields(simple_schema):
    document = {'b': False, 'i': 0, 'f': 0.0, 'l': 0L, 's': u''}
    data = {'b': True, 'i': u"0", 's': 0}
    with pytest.raises(ValidationError) as info:
        simple_schema.patch(document, data)
    assert info.value.reason == {'i': u"Wrong type. Must be int.",
                                 's': u"Wrong type. Must be string."}
