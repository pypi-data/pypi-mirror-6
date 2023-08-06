"""
    schemes.abstract
    ~~~~~~~~~~~~~~~~
"""

import abc

missing = object()


class Element(object):
    """An abstract schema element."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def coerce(self, value):
        """Convert a raw value to a document value."""

    @abc.abstractmethod
    def emit(self, value):
        """Convert the value for output."""

    @property
    def embedded(self):
        return self

    @abc.abstractmethod
    def _accept(self, value, creating):
        """Validate and if necessary convert the given value."""


class Field(Element):
    """An abstract field."""

    def __init__(self):
        self.rules = [self._handle_empty, self._handle_type]

    def coerce(self, value):
        return value

    def emit(self, value):
        return value

    def _handle_empty(self, value, creating):
        if value is missing:
            raise (ValidationError(u"Field is missing.")
                   if creating else SkipElement())
        if value is None:
            raise ValidationError(u"Field cannot be null.")
        return value

    def _accept(self, value, creating):
        for rule in self.rules:
            value = rule(value, creating)
        return value

    def _handle_type(self, value, creating):
        if not isinstance(value, self._class):
            raise ValidationError(self._type_error_message)
        return value

    @property
    def _type_error_message(self):
        return u"Wrong type. Must be " + type(self).__name__.lower() + u"."


class RangedField(Field):
    """A field supporting range validation."""

    def __init__(self, min_value=None, max_value=None):
        super(RangedField, self).__init__()
        if min_value is not None:
            self.rules.append(self._handle_min_value)
        if max_value is not None:
            self.rules.append(self._handle_max_value)
        self.min_value = min_value
        self.max_value = max_value

    def _handle_max_value(self, value, creating):
        if value > self.max_value:
            raise ValidationError(u"Too high. Maximum valid value is " +
                                  unicode(self.emit(self.max_value)) + u".")
        return value

    def _handle_min_value(self, value, creating):
        if value < self.min_value:
            raise ValidationError(u"Too low. Minimum valid value is " +
                                  unicode(self.emit(self.min_value)) + u".")
        return value


class SequenceField(Field):
    """A field supporting length validation."""

    def __init__(self, min_length=None, max_length=None):
        super(SequenceField, self).__init__()
        if min_length is not None:
            self.rules.append(self._handle_min_length)
        if max_length is not None:
            self.rules.append(self._handle_max_length)
        self.min_length = min_length
        self.max_length = max_length

    def _handle_max_length(self, value, creating):
        if len(value) > self.max_length:
            raise ValidationError(u"Too long. Maximum valid length is " +
                                  unicode(self.max_length) + u".")
        return value

    def _handle_min_length(self, value, creating):
        if len(value) < self.min_length:
            raise ValidationError(u"Too short. Minimum valid length is " +
                                  unicode(self.min_length) + u".")
        return value


class ValidationError(Exception):
    """A validation error."""

    @property
    def reason(self):
        return self.args[0]


class SkipElement(Exception):
    """Skip processing the current element."""
