import os

import tornado.ioloop
import tornado.web

from .WebServer import WebServer
from .WebSocket import WebSocket
from lovelib.server import LoveServer


def run():
    application = tornado.web.Application([
        (r"/ws", WebSocket),
        (r"/.*", WebServer),
    ])
    application.listen(8001)
    print("Starting server %s" % application)

    io_loop = tornado.ioloop.IOLoop.current()
    LoveServer.instance().main_thread = io_loop
    io_loop.start()
