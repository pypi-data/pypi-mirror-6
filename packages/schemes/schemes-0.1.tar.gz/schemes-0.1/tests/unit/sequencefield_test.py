"""
    tests.unit.sequencefield_test
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.abstract import ValidationError
from schemes.fields import String, List


def slist(**kwargs):
    return List(String(), **kwargs)


@pytest.mark.parametrize('factory,sequence,reason', (
    (String, u'Hello!', u"Too short. Minimum valid length is 6."),
    (slist, list(u'Hello!'), u"Too short. Minimum valid length is 6.")))
@pytest.mark.parametrize('creating', (True, False))
def test_optionally_rejects_too_short_values(
        factory, sequence, reason, creating):
    field = factory(min_length=len(sequence))
    assert field._accept(sequence, creating) == sequence
    with pytest.raises(ValidationError) as info:
        field._accept(sequence[:-2], creating)
    assert info.value.reason == reason


@pytest.mark.parametrize('factory,sequence,reason', (
    (String, u'Hello!', u"Too long. Maximum valid length is 5."),
    (slist, list(u'Hello!'), u"Too long. Maximum valid length is 5.")))
@pytest.mark.parametrize('creating', (True, False))
def test_optionally_rejects_too_long_values(
        factory, sequence, reason, creating):
    field = factory(max_length=len(sequence) - 1)
    assert field._accept(sequence[:-2], creating) == sequence[:-2]
    with pytest.raises(ValidationError) as info:
        field._accept(sequence, creating)
    assert info.value.reason == reason
