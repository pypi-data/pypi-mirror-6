"""
    tests.integration.writeonly_fields_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError


def test_patch_fails_with_missing_fields_in_writeonly_embedded(
        writeonly_schema):
    embedded = {'b': False, 'i': 42, 'f': 42.42, 'l': 42L, 's': u'Hello'}
    document = {'public': 0, 'wo': embedded}
    data = {'public': 1, 'wo': {'b': True, 'f': 42.42, 'l': 42L}}
    with pytest.raises(ValidationError) as info:
        writeonly_schema.patch(document, data)
    assert info.value.reason == {'wo': {'i': u"Field is missing.",
                                        's': u"Field is missing."}}
