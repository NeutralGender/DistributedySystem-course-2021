from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import pika
import logging
import http.client
import simplejson as json

dictionary = dict()

def consum_queue(dictionary):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel();
    for method_frame, properties, body in channel.consume('lab6'):
        pair = json.loads( body )
        print(pair)
        dictionary[ pair['id'] ] = pair['data']
        print(list(dictionary.values()))
        
class S(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def do_GET(self):
        self._set_response()
        message = json.dumps( list( dictionary.values() ) )
        self.wfile.write(bytes(message, "utf8"))
    
    def do_POST(self):
        self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=8082):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    thread = threading.Thread(target=consum_queue, args=(dictionary,))
    thread.start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')
    thread.join()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
