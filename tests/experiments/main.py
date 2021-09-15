from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

from test_tools import logger, World


class HttpRequestHandler(BaseHTTPRequestHandler):
    def do_PUT(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        logger.info(f'PUT from {self.client_address}: {post_data}')

        self.__set_response()

    def __set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"PUT request for {self.path}".encode('utf-8'))


close_node_event = threading.Event()


def node_run_thread_body(server_port):
    logger.info('Thread started')
    with World() as world:
        init_node = world.create_init_node()
        init_node.config.notifications_endpoint = f'127.0.0.1:{server_port}'
        init_node.config.log_logger = '{"name":"default","level":"all","appender":"stderr"} {"name":"user","level":"all","appender":"stderr"} {"name":"p2p","level":"all","appender":"p2p"}'
        init_node.run()

        logger.info('Waiting...')
        close_node_event.wait()
        logger.info('Received close_node_event')
    logger.info('Thread finished')


if __name__ == '__main__':
    # with World() as world:
    #     init_node = world.create_init_node()
    #     init_node.run()
    #
    #     while True:
    #         pass
    # exit()

    logger.info('started')
    server_address = ('127.0.0.1', 0)
    server = HTTPServer(server_address, HttpRequestHandler)

    logger.info(f'Server port: {server.server_port}')
    node_run_thread = threading.Thread(target=node_run_thread_body, args=(server.server_port,))
    node_run_thread.start()

    try:
        server.serve_forever(1.0)
    finally:
        logger.info('(In finally)')
        #server.server_close()
        close_node_event.set()

# Wisi na:
# futex(
#   0x5637a1eda02c,
#   FUTEX_WAIT_BITSET_PRIVATE|FUTEX_CLOCK_REALTIME,
#   0,
#   {tv_sec=1631617200, tv_nsec=25},
#   0xffffffff
# ) = ?
