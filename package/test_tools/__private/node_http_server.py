from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from typing import Any, Optional

from test_tools.__private.raise_exception_helper import RaiseExceptionHelper
import test_tools as tt

class NodeHttpServer:
    __ADDRESS = ("127.0.0.1", 0)

    class __HttpServer(HTTPServer):
        def __init__(self, server_address, request_handler_class, parent):
            super().__init__(server_address, request_handler_class)
            self.parent = parent

        def notify(self, message):
            self.parent.notify(message)

    def __init__(self, observer, *, name: str):
        self.__observer = observer

        self.__name = name
        self.__server = None
        self.__thread: Optional[threading.Thread] = None

    @property
    def port(self) -> int:
        if self.__server is None:
            self.__server = self.__HttpServer(self.__ADDRESS, HttpRequestHandler, self)

        return self.__server.server_port

    def run(self):
        tt.logger.info(f"run0 :{self.__thread}")
        if self.__thread is not None:
            tt.logger.info(f"run1 :{self.__thread}")
            raise RuntimeError("Server is already running")

        tt.logger.info(f"run2 :{self.__thread}")
        if self.__server is None:
            self.__server = self.__HttpServer(self.__ADDRESS, HttpRequestHandler, self)
        tt.logger.info(f"run3 :{self.__thread}")
        self.__thread = threading.Thread(target=self.__thread_function, name=self.__name, daemon=True)
        self.__thread.start()

    def __thread_function(self):
        try:
            self.__server.serve_forever()
        except Exception as exception:  # pylint: disable=broad-except
            RaiseExceptionHelper.raise_exception_in_main_thread(exception)

    def close(self):
        tt.logger.info(f"close0 :{self.__thread}")
        if self.__thread is None:
            tt.logger.info(f"close1 :{self.__thread}")
            return

        self.__server.shutdown()
        self.__server.server_close()
        self.__server = None

        tt.logger.info(f"close2 :{self.__thread}")
        self.__thread.join(timeout=2.0)
        tt.logger.info(f"close3 :{self.__thread}")
        if self.__thread.is_alive():
            tt.logger.info(f"close4 :{self.__thread}")
            raise RuntimeError("Unable to join server thread")
        tt.logger.info(f"close5 :{self.__thread}")
        self.__thread = None
        tt.logger.info(f"close5 :{self.__thread}")

    def notify(self, message):
        """Should be called only by request handler when request is received"""
        self.__observer.notify(message)


class HttpRequestHandler(BaseHTTPRequestHandler):
    server: NodeHttpServer

    def do_PUT(self):  # pylint: disable=invalid-name
        content_length = int(self.headers["Content-Length"])
        message = self.rfile.read(content_length)
        self.server.notify(json.loads(message))

        self.__set_response()

    def log_message(self, format: str, *args: Any) -> None:  # pylint: disable=redefined-builtin
        # This method is defined to silent logs printed after each received message.
        # Solution based on: https://stackoverflow.com/a/3389505
        pass

    def __set_response(self):
        self.send_response(HTTPStatus.NO_CONTENT)
