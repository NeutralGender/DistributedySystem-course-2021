from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import simplejson as json
import uuid

class S(BaseHTTPRequestHandler):

    dictionary = dict()

    def save_to_dictionary(self, post_data):
        pair = json.loads( post_data )
        #S.dictionary[ str( uuid.uuid4() ) ] = post_data
        S.dictionary[ pair[0] ] = pair[1]
        print(S.dictionary)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        message = json.dumps( list( S.dictionary.values() ) )
        self.wfile.write(bytes(message, "utf8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        self.save_to_dictionary( post_data )
        self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=8081):
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
