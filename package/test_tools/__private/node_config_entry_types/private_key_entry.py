from typing import Optional, Union

from test_tools.__private.keys import PrivateKey as PrivateKeyType
from test_tools.__private.node_config_entry_types.config_entry import ConfigEntry
from test_tools.__private.node_config_entry_types.string_entry import String


class PrivateKey(ConfigEntry):
    def __init__(self, value: Optional[Union[str, PrivateKeyType]] = None):
        # pylint: disable=useless-super-delegation
        # This method is defined to provide more detailed parameters type annotations

        super().__init__(value)

    parse_from_text = String.parse_from_text
    serialize_to_text = String.serialize_to_text

    @classmethod
    def _validate(cls, value):
        cls._validate_type(value, [str, PrivateKeyType, type(None)])
