from typing import Optional, TYPE_CHECKING

from test_tools.__private.logger.levels import UserLevel as PredefinedLevels
from test_tools.__private.scope.scope_singleton import context

if TYPE_CHECKING:
    from test_tools.__private.logger.logger_wrapper import LoggerWrapper


class LoggerInterfaceBase:
    level = PredefinedLevels

    def __init__(self, instance: Optional["LoggerWrapper"] = None, *, message_prefix: str = ""):
        self._message_prefix = message_prefix
        self.__instance: Optional["LoggerWrapper"] = instance

    @property
    def _logger(self) -> "LoggerWrapper":

        x = self.__instance if self.__instance is not None else context.get_logger()
        return x

    def debug(self, message: str, stacklevel: int = 1):
        self._logger.debug(f"{self._message_prefix}{message}", stacklevel=stacklevel + 1)

    def info(self, message: str, stacklevel: int = 1):
        self._logger.info(f"{self._message_prefix}{message}", stacklevel=stacklevel + 1)

    def warning(self, message: str, stacklevel: int = 1):
        self._logger.warning(f"{self._message_prefix}{message}", stacklevel=stacklevel + 1)

    def error(self, message: str, stacklevel: int = 1):
        self._logger.error(f"{self._message_prefix}{message}", stacklevel=stacklevel + 1)

    def critical(self, message: str, stacklevel: int = 1):
        self._logger.critical(f"{self._message_prefix}{message}", stacklevel=stacklevel + 1)

    def set_level(self, level_: level) -> None:
        """
        Allow to select, which logs should be printed on stdout and to file. All logs with importance lower than given
        in `level_` parameter will be ignored; all with equal or higher will be registered.

        For example this is how logs level can be set to debug: `tt.logger.set_level(tt.logger.level.DEBUG)`.
        """
        self._logger.set_stream_handler_level(level_)
        self._logger.set_file_handler_level(level_)
