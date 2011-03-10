# -*- coding: utf-8 -*-
import ConfigParser
import os
import re

import tornado.httpserver
import tornado.ioloop
import tornado.web

from src.netineti import NetiNetiTrain, NameFinder

path =  os.path.abspath(os.path.dirname(__file__))

config = ConfigParser.ConfigParser()
config.read(path + '/config/neti_http_config.cfg')
HOST = config.get('http_settings', 'host')
PORT = int(config.get('http_settings', 'port'))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('hello world')

    def post(self):
        self.set_header('Content-type', 'text/plain')
        data = self.get_argument('data')
        try:
          from_web_form = self.get_arguments('from_web_form')
        except:
          from_web_form = 'false'
        names = nf.find_names(data, resolvedot=True)


        if from_web_form[0] == 'true':
          results = names[0]
        else:
          #pretty_names_list = names[0].split("\n")
          full_names_list = names[1]
          offsets = names[2]
          
          #since full_names_list and offsets are in a 1:1 correspondence, this should work
          if len(full_names_list) == len(offsets):
              results = '|'.join(["%s,%d" % (re.sub('/\s/', '', name),offsets[i][0]) for i, name in enumerate(full_names_list)])
          else:
              raise Exception

        self.write(results)

if __name__ == '__main__':
    nf = NameFinder(NetiNetiTrain())
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(PORT)
    print('Starting server, use <Ctrl-C> to stop')
    tornado.ioloop.IOLoop.instance().start()

