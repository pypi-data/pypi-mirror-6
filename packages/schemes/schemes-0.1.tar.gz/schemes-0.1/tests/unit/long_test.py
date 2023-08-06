"""
    tests.unit.long_test
    ~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.fields import Long


def test_emits_value_transformed_to_unicode_string():
    field = Long()
    assert field.emit(4242424242L) == u'4242424242'


@pytest.mark.parametrize('value,expected', ((42, 42L),
                                            (u'4242424242', 4242424242L)))
@pytest.mark.parametrize('creating', (True, False))
def test_accepts_a_value_compatible_with_long(value, expected, creating):
    field = Long()
    assert field._accept(value, creating) == expected
