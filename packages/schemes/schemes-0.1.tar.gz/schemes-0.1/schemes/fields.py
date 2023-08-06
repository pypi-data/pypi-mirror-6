"""
    schemes.fields
    ~~~~~~~~~~~~~~
"""

from re import compile as _compile

from schemes.abstract import (
    Field as _Field,
    RangedField as _RangedField,
    SequenceField as _SequenceField,
    ValidationError as _ValidationError)


class Bool(_Field):
    """A boolean field."""
    _class = bool


class Int(_RangedField):
    """An integer field."""
    _class = int


class Float(_RangedField):
    """A float field."""
    _class = float


class Long(_RangedField):
    """A long field."""

    def emit(self, value):
        return unicode(value)

    def _handle_type(self, value, creating):
        if isinstance(value, bool):
            raise _ValidationError(self._type_error_message)
        try:
            return long(value)
        except (TypeError, ValueError):
            raise _ValidationError(self._type_error_message)


class String(_SequenceField):
    """A unicode string field."""
    _class = unicode

    def __init__(self, regex=None, min_length=None, max_length=None):
        super(String, self).__init__(
            min_length=min_length, max_length=max_length)
        if regex is not None:
            self.rules.append(self._handle_regex)
        self.regex = (_compile(regex) if isinstance(regex, unicode) else regex)

    def _handle_regex(self, value, creating):
        if not self.regex.search(value):
            raise _ValidationError(u"Malformed input string.")
        return value


class List(_SequenceField):
    """A list of typed elements."""
    _class = list

    def __init__(self, element, min_length=None, max_length=None):
        super(List, self).__init__(
            min_length=min_length, max_length=max_length)
        self.rules.append(self._handle_items)
        self.element = element.embedded

    def coerce(self, value):
        for index, item in enumerate(value):
            value[index] = self.element.coerce(item)
        return value

    def emit(self, value):
        return [self.element.emit(each) for each in value]

    def _handle_items(self, value, creating):
        errors = {}
        for index, item in enumerate(value):
            try:
                value[index] = self.element._accept(item, creating)
            except _ValidationError as error:
                errors[index] = error.reason
        if errors:
            raise _ValidationError(errors)
        return value
