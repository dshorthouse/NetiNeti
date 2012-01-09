# -*- coding: utf-8 -*-
import ConfigParser
import os
import re

import tornado.httpserver
import tornado.ioloop
import tornado.web

from src.neti_neti import NetiNeti
from src.neti_neti_trainer import NetiNetiTrainer

path =  os.path.abspath(os.path.dirname(__file__))

config = ConfigParser.ConfigParser()
config.read(path + '/config/neti_http_config.cfg')
HOST = config.get('http_settings', 'host')
PORT = int(config.get('http_settings', 'port'))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<a href="http://en.wikipedia.org/wiki/Neti_neti">नेति नेति</a>')

    def post(self):
        self.set_header('Content-type', 'text/plain')
        data = self.get_argument('data')
        try:
          from_web_form = self.get_arguments('from_web_form')
        except:
          from_web_form = 'false'
        names = nn.find_names(data, resolve_abbreviated = True)
        print names

        if from_web_form == 'true':
          results = names[0]
        else:
          #pretty_names_list = names[0].split("\n")
          full_names_list = names[1]
          offsets = names[2]
          
          #since full_names_list and offsets are in a 1:1 correspondence, this should work
          print full_names_list
          print offsets
          if len(full_names_list) == len(offsets):
              results = '|'.join(["%s,%s,%s" % (re.sub('/\s/', '', name), offsets[i][0], offsets[i][1]) for i, name in enumerate(full_names_list)])
          else:
              raise Exception

        self.write(results)

if __name__ == '__main__':
    print ("Training NetiNeti, it will take a while...")
    nnt = NetiNetiTrainer()
    nn = NetiNeti(nnt)
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    print('Starting server, use <Ctrl-C> to stop')
    tornado.ioloop.IOLoop.instance().start()

