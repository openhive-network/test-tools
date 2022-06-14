from pprint import pprint
from typing import Any

import pytest

from test_tools.__private.configuration.experimental_config import Config
from test_tools.__private.scope import current_scope


class ConfigWrapper:
    def __init__(self, config: Config):
        self.__config = config

    def __getattr__(self, name: str) -> Any:
        return self.__config._Config__dynaconf[name]


@pytest.fixture(autouse=True, scope='package')
def config(request):
    config = current_scope.context._Context__config
    config_wrapped = ConfigWrapper(config)
    a = config._Config__already_loaded_paths

    return config_wrapped
