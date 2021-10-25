from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from datetime import datetime
import json

from test_tools import logger


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args):
        BaseHTTPRequestHandler.__init__(self, *args)
        self.__timestamp = None

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        timestamp = self.__timestamp or datetime.now().timestamp()
        json_to_pass = json.dumps(timestamp)
        self.wfile.write(json_to_pass.encode('utf-8'))

    def set_timestamp(self, timestamp):
        self.__timestamp = timestamp


class TimeServer:
    def __init__(self):
        self.__server_address = None
        self.__server = None
        self.__thread = None
        self.__timestamp = None

    def run(self, port = 8080):
        self.__server_address = ('', port)
        def handler_factory():
            handler = RequestHandler()
            handler.set_timestamp(self.__timestamp)
            return handler

        self.__server = HTTPServer(self.__server_address, handler_factory)
        self.__thread = Thread(target=self.__server.serve_forever)
        self.__thread.daemon = True
        logger.info('Starting httpd...')
        self.__thread.start()

    def close(self):
        pass

    def set_timestamp(self, timestamp):
        self.__timestamp = timestamp
