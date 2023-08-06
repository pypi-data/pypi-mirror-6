"""
    schemes.timefields
    ~~~~~~~~~~~~~~~~~~
"""

from datetime import date as _date, datetime as _datetime

from schemes.abstract import (
    RangedField as _RangedField,
    ValidationError as _ValidationError)
from schemes.libs.rfc3339 import (
    parse_date as _parse_date,
    parse_datetime as _parse_datetime)


class Date(_RangedField):
    """A date field."""

    def emit(self, value):
        return value.isoformat()

    def _handle_type(self, value, creating):
        if isinstance(value, _date):
            return value
        try:
            return _parse_date(value)
        except ValueError:
            raise _ValidationError(u"Not a valid RFC 3339 date.")
        except TypeError:
            raise _ValidationError(self._type_error_message)


class Datetime(_RangedField):
    """A datetime field."""

    def emit(self, value):
        return value.isoformat()

    def _handle_type(self, value, creating):
        if isinstance(value, _datetime):
            return value
        try:
            return _parse_datetime(value)
        except ValueError:
            raise _ValidationError(u"Not a valid RFC 3339 datetime.")
        except TypeError:
            raise _ValidationError(self._type_error_message)
