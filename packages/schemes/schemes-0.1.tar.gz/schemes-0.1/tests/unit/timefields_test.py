"""
    tests.unit.datetime_test
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""

import datetime
import pytest

from schemes.abstract import ValidationError
from schemes.timefields import Date, Datetime
from schemes.libs.rfc3339 import UTC_TZ


fixed_dt = datetime.datetime(2008, 8, 24, 0, 0, tzinfo=UTC_TZ)
fixed_date = fixed_dt.date()


@pytest.mark.parametrize('factory,value,expected', (
    (Datetime, fixed_dt, u'2008-08-24T00:00:00+00:00'),
    (Date, fixed_date, u'2008-08-24')))
def test_emits_value_transformed_to_unicode_string(factory, value, expected):
    field = factory()
    assert field.emit(value) == expected


@pytest.mark.parametrize('factory,value,expected', (
    (Datetime, u'2008-08-24T00:00:00+00:00', fixed_dt),
    (Datetime, u'2008-08-24T00:00:00Z', fixed_dt),
    (Date, u'2008-08-24', fixed_date)))
@pytest.mark.parametrize('creating', (True, False))
def test_accepts_an_RFC3339_formatted_string(
        factory, value, expected, creating):
    field = factory()
    assert field._accept(value, creating) == expected


@pytest.mark.parametrize('factory,message', (
    (Datetime, u"Not a valid RFC 3339 datetime."),
    (Date, u"Not a valid RFC 3339 date.")))
@pytest.mark.parametrize('creating', (True, False))
def test_rejects_an_invalid_string(factory, message, creating):
    field = factory()
    with pytest.raises(ValidationError) as info:
        field._accept(u'now', creating)
    assert info.value.reason == message
