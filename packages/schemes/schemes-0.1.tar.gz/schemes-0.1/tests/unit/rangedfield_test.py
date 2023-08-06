"""
    tests.unit.rangedfield_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import datetime
import pytest

from schemes.abstract import ValidationError
from schemes.fields import Int, Float, Long
from schemes.timefields import Date, Datetime
from schemes.libs.rfc3339 import UTC_TZ

ref_dt = datetime.datetime(2008, 8, 24, 0, 0, tzinfo=UTC_TZ)
early_dt = ref_dt - datetime.timedelta(microseconds=1)
late_dt = ref_dt + datetime.timedelta(microseconds=1)

ref_date = ref_dt.date()
early_date = ref_date - datetime.timedelta(days=1)
late_date = ref_date + datetime.timedelta(days=1)


@pytest.mark.parametrize('factory,low,value,reason', (
    (Int, 1, 0, u"Too low. Minimum valid value is 1."),
    (Long, 1L, 0L, u"Too low. Minimum valid value is 1."),
    (Float, 1.0, 0.99, u"Too low. Minimum valid value is 1.0."),
    (Datetime, ref_dt, early_dt,
        u"Too low. Minimum valid value is 2008-08-24T00:00:00+00:00."),
    (Date, ref_date, early_date,
        u"Too low. Minimum valid value is 2008-08-24.")))
@pytest.mark.parametrize('creating', (True, False))
def test_optionally_rejects_values_below_minimum(
        factory, low, value, reason, creating):
    field = factory(min_value=low)
    assert field._accept(low, creating) == low
    with pytest.raises(ValidationError) as info:
        field._accept(value, creating)
    assert info.value.reason == reason


@pytest.mark.parametrize('factory,high,value,reason', (
    (Int, 1, 2, u"Too high. Maximum valid value is 1."),
    (Long, 1L, 2L, u"Too high. Maximum valid value is 1."),
    (Float, 1.0, 1.01, u"Too high. Maximum valid value is 1.0."),
    (Datetime, ref_dt, late_dt,
        u"Too high. Maximum valid value is 2008-08-24T00:00:00+00:00."),
    (Date, ref_date, late_date,
        u"Too high. Maximum valid value is 2008-08-24.")))
@pytest.mark.parametrize('creating', (True, False))
def test_optionally_rejects_values_above_maximum(
        factory, high, value, reason, creating):
    field = factory(max_value=high)
    assert field._accept(high, creating) == high
    with pytest.raises(ValidationError) as info:
        field._accept(value, creating)
    assert info.value.reason == reason
