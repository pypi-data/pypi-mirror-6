"""
    tests.unit
    ~~~~~~~~~~
"""

from schemes.abstract import Element


class FakeField(Element):
    """A fake field to use as a test helper."""
    has_been_embedded = False

    def coerce(self, value):
        if value is None:
            raise ValueError()
        return u'coerce({})'.format(value)

    def emit(self, value):
        if isinstance(value, Exception):
            raise value
        return u'emit({})'.format(value)

    def _accept(self, value, creating):
        if isinstance(value, Exception):
            raise value
        return u'accept({}, {})'.format(value, creating)

    @property
    def embedded(self):
        self.has_been_embedded = True
        return self
