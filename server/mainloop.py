import os

import tornado.ioloop
import tornado.web

from .WebServer import WebServer
from lovelib.server.websocket import LoveBotWebSocket


def run():
    application = tornado.web.Application([
        (r"/ws", LoveBotWebSocket),
        (r"/.*", WebServer),
    ])
    application.listen(8001)
    print("Starting server %s" % application)
    tornado.ioloop.IOLoop.current().start()
