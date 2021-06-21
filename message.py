from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import pika
import logging
import http.client
import simplejson as json
import consul_api
import sys

dictionary = dict()

def get_rabbitmq_config():
    records = json.loads( consul_api.get_kv("rabbitmq")["Value"].decode() )
    for record in records:
        if record['id'] == sys.argv[2]:
            print(record['queue_addr'], record['queue_name'])
            return(record['queue_addr'], record['queue_name'])

def consum_queue(dictionary, queue_address, queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(queue_address))
    channel = connection.channel();
    for method_frame, properties, body in channel.consume(queue_name):
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
        if self.path == '/health':
                self._set_response()
                self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        else:
            self._set_response()
            message = json.dumps( list( dictionary.values() ) )
            self.wfile.write(bytes(message, "utf8"))
    
    def do_POST(self):
        self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=8082):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    
    consul_api.service_registration(service_name = "message",
                                    service_id = ("message_" + str(port)),
                                    service_address = "127.0.0.1",
                                    service_port = port,
                                    service_tags = ('message', 'lab_7', str(port)),
                                    service_interv = '4s')
    queue_config = get_rabbitmq_config()
    print(queue_config)
    thread = threading.Thread(target=consum_queue, args=(dictionary, queue_config[0], queue_config[1],))
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

    if len(argv) == 3:
        run(port=int(argv[1]))
    else:
        run()
