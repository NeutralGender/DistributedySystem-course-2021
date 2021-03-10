from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import simplejson as json


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def request_( self, host, port, method, payload=None ):
        conn = http.client.HTTPConnection( host, port );
        headers = {'Content-type': 'application/json'}
        conn.request(method, '/post', payload, headers)
        return conn.getresponse()

    def do_GET(self):
        response = self.request_('localhost', 8081, "GET",)
        response2 = self.request_('localhost', 8082, "GET",)
        
        self._set_response()
        self.wfile.write( '{0}: {1}\n'.format( response.read().decode(), 
                                               response2.read().decode() ).encode('UTF-8') )

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself
        
        self.request_( 'localhost', 8081, "POST", post_data )
        self.request_('localhost', 8082, "GET",)

        self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
