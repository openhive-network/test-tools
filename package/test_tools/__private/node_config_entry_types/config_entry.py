from abc import ABC, abstractmethod


class ConfigEntry(ABC):
    def __init__(self, value=None):
        self._value = None  # To disable the warning about definition outside of __init__
        self.set_value(value)

    @abstractmethod
    def validate(self, value):
        """Raises exception if value or its type is incorrect."""

    @abstractmethod
    def parse_from_text(self, text):
        ...

    @abstractmethod
    def serialize_to_text(self):
        ...

    def clear(self):
        self.set_value(None)

    def get_value(self):
        return self._value

    def set_value(self, value):
        try:
            self.validate(value)
        except TypeError as error:
            raise ValueError(str(error)) from error

        self._set_value(value)

    def _set_value(self, value):
        self._value = value

    @classmethod
    def _validate_type(cls, value, valid_types):
        if type(value) not in valid_types:
            raise TypeError(f"{valid_types} were expected, but {repr(value)} with type {type(value)} was passed")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.get_value()!r})"
