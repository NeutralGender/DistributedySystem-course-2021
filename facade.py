from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import simplejson as json
import uuid
import random
import pika
import consul_api
import sys

def get_rabbitmq_config():
    records = json.loads( consul_api.get_kv("rabbitmq")["Value"].decode() )
    for record in records:
        if record['id'] == sys.argv[2]:
            return(record['queue_addr'], record['queue_name'])

rabbitmq_config = get_rabbitmq_config()

connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_config[0]))
channel = connection.channel();
channel.queue_declare(queue=rabbitmq_config[1])

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
        if self.path == '/health':
            self._set_response()
            self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        else:
            random_logger = random.choice(consul_api.get_service_by_id("logger"))
            response_loggging = self.request_(random_logger[0], random_logger[1], "GET",)
            
            random_message = random.choice(consul_api.get_service_by_id("message"))
            response_messging = self.request_(random_message[0], random_message[1], "GET",)
            
            self._set_response()
            self.wfile.write( '{0}: {1}\n'.format( response_loggging.read().decode(), 
                                                response_messging.read().decode() ).encode('UTF-8') )
        

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        json_pair = json.dumps( { 'id': str(uuid.uuid4().int), 'data': post_data } )
        print( json_pair )

        random_logger = random.choice(consul_api.get_service_by_id("logger"))
        self.request_( random_logger[0], random_logger[1], "POST", json_pair )
        channel.basic_publish(exchange='', routing_key='lab6', body= json_pair)

        self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    
    consul_api.service_registration(service_name = "facade",
                                    service_id = ("facade_" + str(port)),
                                    service_address = "127.0.0.1",
                                    service_port = port,
                                    service_tags = ('facade', 'lab_7', str(port)),
                                    service_interv = '3s')
        
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 3:
        run(port=int(argv[1]))
    else:
        run()
