import importlib.util
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Union

from dynaconf import Dynaconf


class Config:
    def __init__(self, working_directory: Union[str, Path]):
        # FIXME: Tą zmienną to tak robię do debugowania, żebyśmy mogli łatwo podejrzeć jakie ścieżki się wymyśliły
        possible_config_paths = self.__get_possible_config_paths(working_directory)

        self.__config = Dynaconf(
            preload=[
                'test_tools_config.default.toml',
            ],
            settings_files=possible_config_paths,
            root_path=Path(importlib.util.find_spec(working_directory).origin).parent,
        )

    def __getattr__(self, item: str) -> Any:
        return getattr(self.__config, item)

    @staticmethod
    def __get_possible_config_paths(package: str) -> Iterable[Path]:
        from pathlib import Path
        import importlib.util

        possible_config_paths = []
        while package:
            package_path = Path(importlib.util.find_spec(package).origin).parent.absolute()
            possible_config_paths.extend([
                package_path / 'test_tools_config.loc.toml',
                package_path / 'test_tools_config.toml',
            ])
            package, _, _ = package.rpartition('.')

        return list(reversed(possible_config_paths))


"""
INSIGHTS:

- If we include only one file `.toml` in the settings_files, the `.local.toml` from subdirectory will be ignored if it
  is the only file in that subdirectory. No files will be loaded.
  failing -> [config_tests/configs_hierarchy_tests/test_single_local_config_in_subdirectory]

- If we include both `.toml` and `.local.toml` in the settings_files, the `.local.toml` from subdirectory will be
  failing when we try to merge conf of `.toml` and `.local.toml` in the same directory. content of the `.local.toml`
  will be merged twice.
  failing -> [/config_tests/configs_merging_tests/test_default_and_local_config_in_subdirectoryy]


CURRENT SOLUTION:

- Do not include `.local.toml` in the settings_files. Use other name for the file instead like `.loc.toml`.
  This will resolve both of the above issues.

"""
