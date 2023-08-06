"""
    tests.integration.conftest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import pytest

from schemes.fields import Bool, Int, Float, List, Long, String
from schemes.modifiers import Optional, WriteOnly
from schemes.schema import Schema


@pytest.fixture(scope='session')
def simple_schema():
    return Schema({'b': Bool(), 'i': Int(), 'f': Float(), 'l': Long(),
                   's': String()})


@pytest.fixture(scope='session')
def nested_schema(simple_schema):
    return Schema({'d': simple_schema})


@pytest.fixture(scope='session')
def list_schema(simple_schema):
    return Schema({'d': List(simple_schema)})


@pytest.fixture(scope='session')
def optional_schema(simple_schema):
    return Schema({'nested': Optional(simple_schema),
                   'nullable': Optional(Long()),
                   'nonnullable': Optional(String(), default=u""),
                   'b': Bool()})


@pytest.fixture(scope='session')
def writeonly_schema(simple_schema):
    return Schema({'public': Int(), 'wo': WriteOnly(simple_schema)})
