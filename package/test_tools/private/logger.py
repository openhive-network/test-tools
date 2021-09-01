import logging
from pathlib import Path

from test_tools.constants import LoggingOutgoingRequestPolicy

class Logger:
    def __init__(self):
        self.__directory = Path('logs/')
        self.__stream_handler = None
        self.__file_handler = None

    def __ensure_initialization(self):
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s (%(name)s, %(filename)s:%(lineno)s)')

        if not self.__is_initialized():
            self.__initialize(formatter)
            return

        if self.__file_handler is None:
            self.__initialize_file_handler(formatter)

    def __is_initialized(self):
        return self.__stream_handler is not None

    def __initialize(self, formatter):
        self.__remove_old_log_if_exists()

        logging.root.setLevel(logging.DEBUG)

        self.__initialize_file_handler(formatter)

        # Configure stream handler
        from sys import stdout
        self.__stream_handler = logging.StreamHandler(stdout)
        self.__stream_handler.setFormatter(formatter)
        self.__stream_handler.setLevel(logging.INFO)
        logging.root.addHandler(self.__stream_handler)

        # Suppress debug logs from selected built-in python libraries
        logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)

    def __initialize_file_handler(self, formatter):
        self.__get_log_path().parent.mkdir(exist_ok=True, parents=True)
        self.__file_handler = logging.FileHandler(self.__get_log_path(), mode='w')
        self.__file_handler.setFormatter(formatter)
        self.__file_handler.setLevel(logging.DEBUG)
        logging.root.addHandler(self.__file_handler)

    def __deinitialize_file_handler(self):
        self.__file_handler.close()
        logging.root.removeHandler(self.__file_handler)
        self.__file_handler = None

    def __remove_old_log_if_exists(self):
        try:
            self.__get_log_path().unlink()
        except FileNotFoundError:
            pass

    def __get_log_path(self):
        return self.__directory / 'last_run.log'

    def show_debug_logs_on_stdout(self):
        self.__ensure_initialization()
        __stream_handler.setLevel(logging.DEBUG)

    def set_directory(self, directory):
        if self.__file_handler is not None:
            self.__deinitialize_file_handler()

        self.__directory = Path(directory)

    # Wrapped functions from logging library
    def debug(self, message):
        self.__ensure_initialization()
        logging.debug(message)

    def info(self, message):
        self.__ensure_initialization()
        logging.info(message)

    def warning(self, message):
        self.__ensure_initialization()
        logging.warning(message)

    def error(self, message):
        self.__ensure_initialization()
        logging.error(message)

    def critical(self, message):
        self.__ensure_initialization()
        logging.critical(message)

    def exception(self, message):
        self.__ensure_initialization()
        logging.exception(message)

    def getLogger(self, name):
        self.__ensure_initialization()
        return logging.getLogger(name)

def log_request( policy : LoggingOutgoingRequestPolicy, endpoint : str, data : str = None, method : str = "GET"):
  if LoggingOutgoingRequestPolicy.BASIC_LOGGING == policy:
    message = f"{method} {data} {endpoint}"
  elif LoggingOutgoingRequestPolicy.LOGGING_AS_CURL_REQUEST == policy:
    message = f"curl -X {method} "
    if data is not None:
      message += f"-d '{data}' "
    message += endpoint

  if LoggingOutgoingRequestPolicy.DO_NOT_LOG != policy:
    print(message, flush=True)
