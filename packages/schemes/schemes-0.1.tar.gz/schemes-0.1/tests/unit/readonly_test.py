"""
    tests.unit.readonly_test
    ~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import missing, SkipElement, ValidationError
from schemes.modifiers import ReadOnly, Internal
from tests.unit import FakeField


def test_emits_value_according_to_field_rules():
    field = ReadOnly(FakeField())
    assert field.emit(0) == u'emit(0)'


def test_coerces_value_according_to_field_rules():
    field = ReadOnly(FakeField())
    assert field.coerce(0) == u'coerce(0)'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
def test_accepts_missing_value_as_none_on_create_if_no_create_is_set(modifier):
    field = modifier(FakeField())
    assert field._accept(missing, True) is None


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
def test_accepts_missing_value_as_create_value_on_create(modifier):
    field = modifier(FakeField(), create=u'create')
    assert field._accept(missing, True) == u'create'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
def test_supports_callable_create_value(modifier):
    field = modifier(FakeField(), create=lambda: u'create')
    assert field._accept(missing, True) == u'create'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
def test_skips_value_on_update_if_update_is_not_set(modifier):
    field = modifier(FakeField())
    with pytest.raises(SkipElement):
        field._accept(missing, False)


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
def test_accepts_missing_value_as_update_value_on_update(modifier):
    field = modifier(FakeField(), update=u'update')
    assert field._accept(missing, False) == u'update'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
def test_supports_callable_update_value(modifier):
    field = modifier(FakeField(), update=lambda: u'update')
    assert field._accept(missing, False) == u'update'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
@pytest.mark.parametrize('creating', (True, False))
def test_accepts_missing_value_as_always_value_if_provided(modifier, creating):
    field = modifier(FakeField(), always=u'always')
    assert field._accept(missing, creating) == u'always'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
@pytest.mark.parametrize('creating', (True, False))
def test_supports_callable_always_value(modifier, creating):
    field = modifier(FakeField(), always=lambda: u'always')
    assert field._accept(missing, creating) == u'always'


@pytest.mark.parametrize('modifier', (ReadOnly, Internal))
@pytest.mark.parametrize('creating', (True, False))
def test_rejects_values_other_than_missing(modifier, creating):
    field = modifier(FakeField())
    with pytest.raises(ValidationError) as info:
        field._accept(0, creating)
    assert info.value.reason == u"Field is read-only."
