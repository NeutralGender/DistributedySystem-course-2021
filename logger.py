import hazelcast
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import sys
import simplejson as json
import consul_api

def get_hazelcast_config():
    records = json.loads( consul_api.get_kv("hazelcast")["Value"].decode() )
    for record in records:
        if record['id'] == sys.argv[2]:
            return (record['host'] + ":" + record['port'])

client = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        #f"127.0.0.1:{sys.argv[2]}"
        get_hazelcast_config()
    ]
)

my_map = client.get_map("lab6")

class S(BaseHTTPRequestHandler):

    dictionary = dict()

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
                self._set_response()
                self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        else:
            result = []
            self._set_response()
            
            for record in my_map.entry_set().result():
                result.append(record[1])
            
            self.wfile.write( bytes(json.dumps(result), "utf8") )

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        msg = json.loads( post_data )
        print(post_data)
        my_map.put(msg['id'], msg['data'])
        self._set_response()


def run(server_class=HTTPServer, handler_class=S, port=8081):    
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    
    consul_api.service_registration(service_name = "logger",
                                    service_id = ("logger_" + str(port)),
                                    service_address = "127.0.0.1",
                                    service_port = port,
                                    service_tags = ('logger', 'lab_7', str(port)),
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
        print(str(sys.argv))
        run()
