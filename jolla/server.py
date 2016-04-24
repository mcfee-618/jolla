import gevent.monkey
gevent.monkey.patch_all()

from gevent.pywsgi import WSGIServer
import re

class WebApp():

    urls = []

    def __init__(self, environ):

        self._environ = environ

        self._path = self._environ['PATH_INFO']

        self.request = {}

        self.request['method'] = self._environ['REQUEST_METHOD']
        self.request['data'] = {}
        line = self._environ['QUERY_STRING']
        request_data = environ['wsgi.input'].read()
        if request_data:
            for data_pair in request_data.split('&'):
                key, value = data_pair.split('=')
                self.request['data'][key] = value

    def parse(self):
        for url_handler in self.urls:
            if url_handler[0] == r'/':
                if self._environ['PATH_INFO'] != '/':
                    continue
                else:
                    html_code = url_handler[1]()

            if re.match(self._environ['PATH_INFO'], url_handler[0]):
                html_code = url_handler[1]()
                return html_code
        raise HTTP404Error('REQUEST NOT FOUND IN ROUTE CONFIGURATION')


class jolla_server(WSGIServer):

    def __init__(self, app, port=8000, host="127.0.0.1"):
        self.port = port
        self.host = host
        self.app = app
        WSGIServer.__init__(self, listener=(
            self.host, self.port), application=self.application)

    def application(self,environ, start_response):

        the_app = self.app(environ)

        try:
            html_code = the_app.parse()
            status = '200 OK'
        except HTTP404Error:
            status = '404 NOT FOUND'
            html_code = '404 NOT FOUND'

        header = [
            ('Content-Type', 'text/html')
        ]

        start_response(status, header)

        return html_code

    def run_server(self):
        print "the server is running on the {} in the port {}".format(self.host, self.port)

        self.serve_forever()
