"""
    tests.unit.attrdict_test
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.utils import AttrDict


def test_is_a_dictionary():
    assert issubclass(AttrDict, dict)


def test_support_reading_an_item_using_attribute_access():
    d = AttrDict()
    d['key'] = u'value'
    assert d.key == d['key'] == u'value'


def test_raises_attributeerror_on_attribute_access_to_inexistent_key():
    d = AttrDict()
    with pytest.raises(AttributeError):
        d.key


def test_supports_writing_an_item_using_attribute_access():
    d = AttrDict()
    d.key = u'value'
    assert d['key'] == d.key == u'value'


def test_supports_deleting_an_item_using_attribute_access():
    d = AttrDict()
    d['key'] = u'value'
    del d.key
    with pytest.raises(KeyError):
        d['key']


def test_raises_attributeerror_on_attribute_deletion_of_inexistent_key():
    d = AttrDict()
    with pytest.raises(AttributeError):
        del d.key


def test_copies_itself_as_attrdict():
    d = AttrDict(a=0, b=1, c=2, d=3, e=4, f=5)
    clone = d.copy()
    assert (clone == d) and (clone is not d) and (clone.__class__ is AttrDict)
