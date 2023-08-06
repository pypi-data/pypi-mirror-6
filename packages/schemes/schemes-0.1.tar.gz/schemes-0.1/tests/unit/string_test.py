"""
    tests.unit.string_test
    ~~~~~~~~~~~~~~~~~~~~~~
"""

import re
import pytest

from schemes.abstract import ValidationError
from schemes.fields import String


@pytest.mark.parametrize('regex', (u'a+b', re.compile(u'a+b')))
@pytest.mark.parametrize('creating', (True, False))
def test_optionally_searches_against_regular_expression(regex, creating):
    field = String(regex=regex)
    assert field._accept(u'Maab', creating) == u'Maab'
    with pytest.raises(ValidationError) as info:
        field._accept(u'aa', creating)
    assert info.value.reason == u"Malformed input string."
