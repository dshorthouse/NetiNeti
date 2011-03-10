import ConfigParser
import time
import cgi
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

from src.netineti import NetiNetiTrain, nameFinder

config = ConfigParser.ConfigParser()
config.read('config/neti_http_config.cfg')
HOST = config.get('http_settings', 'host')
PORT = int(config.get('http_settings', 'port'))

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('hello world')

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        self.send_response(200)
        self.end_headers()
        self.wfile.write(nf.find_names(form['data'].value))
        return

def run(server_class=HTTPServer,
        handler_class=MyHandler):
    server_address = (HOST, PORT)
    print('Starting server, use <Ctrl-C> to stop')
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    NN = NetiNetiTrain()
    nf = nameFinder(NN)
    run()
