"""
    schemes.modifiers
    ~~~~~~~~~~~~~~~~~
"""

from schemes.abstract import (
    missing as _missing,
    Element as _Element,
    SkipElement as _SkipElement,
    ValidationError as _ValidationError)


def _skip():
    raise _SkipElement()


class Modifier(_Element):
    """An abstract schema element modifier."""

    def __init__(self, element):
        self.element = element.embedded

    def coerce(self, value):
        return self.element.coerce(value)

    def emit(self, value):
        return self.element.emit(value)


class Optional(Modifier):
    """An optional schema element."""

    def __init__(self, element, default=None):
        super(Optional, self).__init__(element)
        self.default = default if callable(default) else lambda: default
        self.is_nullable = default is None

    def coerce(self, value):
        return None if value is None else self.element.coerce(value)

    def _accept(self, value, creating):
        if value is _missing and creating:
            return self.default()
        if value is None and self.is_nullable:
            return None
        return self.element._accept(value, creating)


class ReadOnly(Modifier):
    """A read-only schema element."""

    def __init__(self, element, create=None, update=_skip, always=_missing):
        super(ReadOnly, self).__init__(element)
        if always is not _missing:
            create = update = always
        self.create = create if callable(create) else lambda: create
        self.update = update if callable(update) else lambda: update

    def _accept(self, value, creating):
        if value is not _missing:
            raise _ValidationError(u"Field is read-only.")
        return self.create() if creating else self.update()


class WriteOnly(Modifier):
    """A write-only schema element."""

    def emit(self, value):
        raise _SkipElement()

    def _accept(self, value, creating):
        return self.element._accept(value, creating)


class Internal(ReadOnly, WriteOnly):
    """An internal schema element."""
