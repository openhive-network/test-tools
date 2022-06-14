import importlib.util
from pathlib import Path
from typing import Any
from typing import Final
from typing import Iterable
from typing import List
from typing import Union

from dynaconf import Dynaconf  # typing: ignore


class Config:
    DEFAULT_CONFIG_NAME: Final[Path] = Path('test_tools_config.toml')

    def __init__(self):
        default_paths = self.__get_default_config_paths()
        self.__already_loaded_paths = list(default_paths)

        self.__dynaconf = Dynaconf(settings_files=default_paths)
        self.__registered_options = set(self.__dynaconf.as_dict().keys())

    def __getitem__(self, item: str) -> Any:
        if item in self.__registered_options:
            return self.__dynaconf[item]

        raise AttributeError(f'Config has no attribute {item}')

    @staticmethod
    def __get_default_config_paths() -> Iterable[Path]:
        default_tt_config_path = (
            Path(importlib.util.find_spec('test_tools').origin).parent.parent.parent / Config.DEFAULT_CONFIG_NAME
        )

        default_home_config_path = Path.home() / Config.DEFAULT_CONFIG_NAME

        return [default_tt_config_path, default_home_config_path]

    def load_from_package(self, package_path: str) -> None:
        possible_config_paths = self.__get_possible_config_paths(package_path)

        for path in possible_config_paths:
            if path not in self.__already_loaded_paths:
                self.__dynaconf.load_file(path)
                self.__registered_options.update(self.__dynaconf.as_dict().keys())
                self.__already_loaded_paths.append(path)

    @staticmethod
    def __get_possible_config_paths(package: str) -> Iterable[Path]:
        possible_config_paths = []
        while package:
            package_path = Path(importlib.util.find_spec(package).origin).parent.absolute()

            config_local_path = package_path / f'{Config.DEFAULT_CONFIG_NAME.stem}.loc.toml'
            config_path = package_path / Config.DEFAULT_CONFIG_NAME
            possible_config_paths.extend([config_local_path, config_path])

            package, _, _ = package.rpartition('.')

        return list(reversed(possible_config_paths))
