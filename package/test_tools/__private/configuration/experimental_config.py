from pathlib import Path
from typing import Any, Union

from dynaconf import Dynaconf


class Config:
    def __init__(self, working_directory: Union[str, Path]):
        self.__config = Dynaconf(settings_files=[Path(working_directory) / f'test_tools_config.toml'])
        print()

    def __getattr__(self, item: str) -> Any:
        return getattr(self.__config, item)
