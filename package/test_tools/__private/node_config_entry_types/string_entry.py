from typing import Optional

from test_tools.__private.node_config_entry_types.config_entry import ConfigEntry


class String(ConfigEntry):
    def __init__(self, value: Optional[str] = None):
        # pylint: disable=useless-super-delegation
        # This method is defined to provide more detailed parameters type annotations

        super().__init__(value)

    def parse_from_text(self, text: str) -> str:
        self.set_value(text)
        return self._value

    def serialize_to_text(self) -> str:
        return self._value

    @classmethod
    def validate(cls, value):
        cls._validate_type(value, [str, type(None)])
