"""
    tests.unit.field_test
    ~~~~~~~~~~~~~~~~~~~~~
"""

import datetime as dt
import pytest

from schemes.abstract import missing, SkipElement, ValidationError
from schemes.fields import Bool, Float, Int, Long, List, String
from schemes.timefields import Datetime, Date
from schemes.schema import Schema


list_factory = lambda: List(Bool)
schema_factory = lambda: Schema({})
embedded_schema_factory = lambda: schema_factory().embedded


all_fields = (Bool, Float, Int, Long, String, Datetime, Date,
              list_factory, schema_factory, embedded_schema_factory)


@pytest.mark.parametrize('factory,value', ((Bool, False),
                                           (Float, 42.42),
                                           (Int, 42),
                                           (String, u'A string')))
def test_emits_value_without_transform(factory, value):
    field = factory()
    assert field.emit(value) is value


@pytest.mark.parametrize('factory,value', ((Bool, False),
                                           (Float, 42.42),
                                           (Int, 42),
                                           (Long, 424242L),
                                           (String, u'A string')))
def test_coerces_value_without_transform(factory, value):
    field = factory()
    assert field.coerce(value) is value


@pytest.mark.parametrize('factory,value', ((Bool, False),
                                           (Float, 42.42),
                                           (Int, 42),
                                           (Long, 42424242L),
                                           (String, u'A string'),
                                           (Datetime, dt.datetime.now()),
                                           (list_factory, []),
                                           (schema_factory, {}),
                                           (embedded_schema_factory, {})))
@pytest.mark.parametrize('creating', (True, False))
def test_accepts_a_value_of_the_appropriate_type(factory, value, creating):
    field = factory()
    assert field._accept(value, creating) == value


@pytest.mark.parametrize('factory,value,reason', (
    (Bool, 1, u"Wrong type. Must be bool."),
    (Bool, u'true', u"Wrong type. Must be bool."),
    (Float, 42, u"Wrong type. Must be float."),
    (Float, u'42.42', u"Wrong type. Must be float."),
    (Int, 42.0, u"Wrong type. Must be int."),
    (Int, u'42', u"Wrong type. Must be int."),
    (Long, u'A string', u"Wrong type. Must be long."),
    (Long, [], u"Wrong type. Must be long."),
    (Long, False, u"Wrong type. Must be long."),
    (String, 42, u"Wrong type. Must be string."),
    (Datetime, 42, u"Wrong type. Must be datetime."),
    (list_factory, u"A string", u"Wrong type. Must be list."),
    (schema_factory, [], u"Wrong type. Must be mapping."),
    (embedded_schema_factory, [], u"Wrong type. Must be mapping.")))
@pytest.mark.parametrize('creating', (True, False))
def test_rejects_a_value_of_inappropriate_type(
        factory, value, reason, creating):
    field = factory()
    with pytest.raises(ValidationError) as info:
        field._accept(value, creating)
    assert info.value.reason == reason


@pytest.mark.parametrize('factory', all_fields)
@pytest.mark.parametrize('creating', (True, False))
def test_rejects_none(factory, creating):
    field = factory()
    with pytest.raises(ValidationError) as info:
        field._accept(None, creating)
    assert info.value.reason == u"Field cannot be null."


@pytest.mark.parametrize('factory', all_fields)
def test_rejects_missing_value_on_creation(factory):
    field = factory()
    with pytest.raises(ValidationError) as info:
        field._accept(missing, True)
    assert info.value.reason == u"Field is missing."


@pytest.mark.parametrize('factory', all_fields)
def test_skips_missing_value_on_update(factory):
    field = factory()
    with pytest.raises(SkipElement):
        field._accept(missing, False)
