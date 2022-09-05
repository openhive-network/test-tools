from typing import Optional, TYPE_CHECKING

from test_tools.__private.scope.scope_singleton import context

if TYPE_CHECKING:
    from test_tools.__private.logger.logger_wrapper import LoggerWrapper


class LoggerInterfaceBase:
    def __init__(self, instance: Optional['LoggerWrapper'] = None, *, message_prefix: str = ''):
        self.__message_prefix = message_prefix
        self.__instance: Optional['LoggerWrapper'] = instance

    @property
    def _logger(self) -> 'LoggerWrapper':
        return self.__instance if self.__instance is not None else context.get_logger()

    def debug(self, message: str):
        self._logger.debug(f'{self.__message_prefix}{message}', stacklevel=self.__number_of_stack_frames_to_skip)

    def info(self, message: str):
        self._logger.info(f'{self.__message_prefix}{message}', stacklevel=self.__number_of_stack_frames_to_skip)

    def warning(self, message: str):
        self._logger.warning(f'{self.__message_prefix}{message}', stacklevel=self.__number_of_stack_frames_to_skip)

    def error(self, message: str):
        self._logger.error(f'{self.__message_prefix}{message}', stacklevel=self.__number_of_stack_frames_to_skip)

    def critical(self, message: str):
        self._logger.critical(f'{self.__message_prefix}{message}', stacklevel=self.__number_of_stack_frames_to_skip)

    @property
    def __number_of_stack_frames_to_skip(self) -> int:
        """
        Returns number of stack frames which internal logger `__instance` should skip to figure out caller file and line
        number. See test_tools/package/test_tools/__private/logger/readme.md for details.
        """
        return 2
