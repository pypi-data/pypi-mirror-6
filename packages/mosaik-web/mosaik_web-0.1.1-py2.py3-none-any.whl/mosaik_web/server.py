"""
This module contains a simple simpy.io based webserver with websockets.

"""
import json
import logging
import mimetypes
import os.path

from simpy.io import select as backend
from simpy.io.http import Service
from simpy.io.websocket import WebSocket


logger = logging.getLogger(__name__)


class Server(object):
    def __init__(self, env, server_sock):
        self.env = env
        self.server_sock = server_sock

        self.basedir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    'html'))
        """Base directory for static files."""

        self.topology_ready = env.event()
        self.topology = None

        self.new_data = env.event()
        """This event is triggered by the mosaik API if new data is available.
        """

        self.env.process(self._serve())

    def _serve(self):
        """Webserver main process."""
        while True:
            sock = yield self.server_sock.accept()
            service = Service(sock)
            self.env.process(self.handler(service))

    def handler(self, service):
        """Handle client requests.

        Either serve static files or create a websocket.

        """
        try:
            while True:
                request = yield service.recv()
                yield request.read(all=True)

                uri = request.uri
                if uri.endswith('/'):
                    uri += 'index.html'

                if uri == '/websocket':
                    self.env.process(self.websock(service, request))
                    break

                try:
                    ctype, data = self.serve_static(uri)
                except ValueError:
                    yield request.respond(404, {
                        'content-type': 'text/plain; charset=utf-8',
                    }, data=b'Not found')
                else:
                    yield request.respond(200, {
                        'content-type': ctype,
                    }, data=data)

        except ConnectionError:
            logger.warn('socket ConnectionError')

    def websock(self, service, request):
        """Process for websocket connections."""
        excess_data = service.decommission()
        socket = WebSocket(service.sock)
        socket.configure(False, headers=request.headers)

        try:
            msg = yield socket.read()
            assert msg == 'get_topology'
            yield self.topology_ready
            yield socket.write(json.dumps(['setup_topology', self.topology]))

            evt_read = socket.read()
            evt_new_data = self.new_data
            while True:
                results = yield evt_read | evt_new_data
                if evt_new_data in results:
                    msg = ['update_data', results[evt_new_data]]
                    yield socket.write(json.dumps(msg))
                    evt_new_data = self.new_data

                if evt_read in results:
                    message = results[evt_read]
                    print(message)
                    yield socket.write('ohai' + message)
                    evt_read = socket.read()

        except ConnectionError:
            logger.warn('websocket ConnectionError')

    def serve_static(self, uri):
        """Try to read and return a static file and its mime type."""
        req_path = os.path.abspath(os.path.join(self.basedir, uri.lstrip('/')))
        if not req_path.startswith(self.basedir):
            raise ValueError
        if not os.path.isfile(req_path):
            raise ValueError

        content_type = mimetypes.guess_type(req_path)[0]
        if content_type.startswith('text/'):
            content_type = '%s; charset=utf-8' % content_type
        return content_type, open(req_path, 'rb').read()

    def set_new_data(self, data):
        old_evt = self.new_data
        self.new_data = self.env.event()
        old_evt.succeed(data)


if __name__ == '__main__':
    addr = ('localhost', 8000)

    env = backend.Environment()
    server_sock = backend.TCPSocket.server(env, addr)
    server = Server(env, server_sock)

    env.run()
