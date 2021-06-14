import hazelcast
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import http.client
import sys
import simplejson as json

client = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        f"127.0.0.1:{sys.argv[2]}"
    ]
)

my_map = client.get_map("lab4")

class S(BaseHTTPRequestHandler):

    dictionary = dict()

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
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
