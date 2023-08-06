"""
    schemes.utils
    ~~~~~~~~~~~~~
"""


class AttrDict(dict):
    """A specialized dict supporting attribute access."""
    __slots__ = ()

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

    def __dir__(self):
        return sorted(set(dir(self.__class__)) | self.viewkeys())

    def copy(self):
        return self.__class__(self)
