from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import simplejson as json
import uuid
import random

LOGGING_PORTS = ('8091', '8092', '8093')

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def _parse_logging_response(self, response):
        result = ""
        print(response)
        for i in response:
            print(i)
            result += json.load(i)['data']
        
        print(result)
        return result

    def request_( self, host, port, method, payload=None ):
        conn = http.client.HTTPConnection( host, port );
        headers = {'Content-type': 'application/json'}
        conn.request(method, '/post', payload, headers)
        return conn.getresponse()

    def do_GET(self):
        response_loggging = self.request_('localhost', random.choice(LOGGING_PORTS), "GET",)
        #response_loggging = self.request_('localhost', 8091, "GET",)
        response_messg_inst = self.request_('localhost', 8082, "GET",)
        
        self._set_response()
        self.wfile.write( '{0}: {1}\n'.format( response_loggging.read().decode(), 
                                               response_messg_inst.read().decode() ).encode('UTF-8') )
        

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        json_pair = json.dumps( { 'id': str(uuid.uuid4().int), 'data': post_data } )
        print( json_pair )

        self.request_( 'localhost', random.choice(LOGGING_PORTS), "POST", json_pair )
        #self.request_( 'localhost', 8091, "POST", json_pair )
        self.request_('localhost', 8082, "POST",)

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
