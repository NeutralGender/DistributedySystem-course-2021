from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import simplejson as json
import uuid
import random
import pika

LOGGING_PORTS = ('8091', '8092', '8093')
MESSAGE_PORTS = ('9091', '9092')

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel();
channel.queue_declare(queue='lab6')

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
        response_messging = self.request_('localhost', random.choice(MESSAGE_PORTS), "GET",)
        response_loggging = self.request_('localhost', random.choice(LOGGING_PORTS), "GET",)
        
        self._set_response()
        self.wfile.write( '{0}: {1}\n'.format( response_loggging.read().decode(), 
                                               response_messging.read().decode() ).encode('UTF-8') )
        

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        json_pair = json.dumps( { 'id': str(uuid.uuid4().int), 'data': post_data } )
        print( json_pair )

        self.request_( 'localhost', random.choice(LOGGING_PORTS), "POST", json_pair )
        channel.basic_publish(exchange='', routing_key='lab6', body= json_pair)

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
