"""
    schemes.schema
    ~~~~~~~~~~~~~~
"""

from schemes.abstract import (
    missing as _missing,
    Element as _Element,
    Field as _Field,
    SkipElement as _SkipElement,
    ValidationError as _ValidationError)
from schemes.utils import AttrDict as _AttrDict


class Schema(_Field):
    """A document schema."""
    _class = dict

    def __init__(self, fields, document_type=_AttrDict):
        super(Schema, self).__init__()
        self.rules.append(self._handle_definition)
        self.fields = SchemaDefinition(fields)
        self.document_type = document_type

    @property
    def embedded(self):
        return Embedded(self)

    def create(self, values):
        return self._accept(values, True)

    def coerce(self, values):
        result = self.document_type()
        for key, element in self.fields:
            result[key] = element.coerce(values[key])
        return result

    def patch(self, document, values):
        document.update(self._accept(values, False))
        return document

    def emit(self, value):
        result = {}
        for key, element in self.fields:
            try:
                result[key] = element.emit(value[key])
            except _SkipElement:
                pass
        return result

    def _handle_definition(self, value, creating):
        result, errors = self.document_type(), {}
        for key, element in self.fields:
            try:
                result[key] = element._accept(value.pop(key, _missing),
                                              creating)
            except _ValidationError as error:
                errors[key] = error.reason
            except _SkipElement:
                pass
        errors.update((key, u"Unexpected field.") for key in value.iterkeys())
        if errors:
            raise _ValidationError(errors)
        return result

    @property
    def _type_error_message(self):
        return u"Wrong type. Must be mapping."


class Embedded(_Element):
    """An embedded document schema."""

    def __init__(self, schema):
        self.schema = schema

    def coerce(self, values):
        return self.schema.coerce(values)

    def emit(self, value):
        return self.schema.emit(value)

    @property
    def document_type(self):
        return self.schema.document_type

    def _accept(self, value, creating):
        if value is _missing and not creating:
            raise _SkipElement()
        return self.schema._accept(value, True)


class SchemaDefinition(object):
    """A container of element definitions."""

    def __init__(self, fields):
        self._fields = {key: element.embedded
                        for key, element in fields.iteritems()}

    def __getattr__(self, name):
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(name)

    def __iter__(self):
        return self._fields.iteritems()
