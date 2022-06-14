from pathlib import Path
from typing import Any, Union

from dynaconf import Dynaconf


class Config:
    def __init__(self, working_directory: Union[str, Path]):
        self.__config = Dynaconf(
            settings_files=[
                'test_tools_config.toml',
                'test_tools_config.loc.toml'
            ],
            root_path=working_directory,
        )
        print()

    def __getattr__(self, item: str) -> Any:
        return getattr(self.__config, item)


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
