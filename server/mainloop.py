import os

import tornado.ioloop
import tornado.web

from lovelib.util import Configuration
from lovelib.server import LoveServer
from .WebServer import WebServer
from .WebSocket import WebSocket


def run(config=None):
    config = config or Configuration.default_configuration()
    LoveServer.instance().set_config(config)

    application = tornado.web.Application([
        (r"/ws", WebSocket),
        (r"/.*", WebServer),
    ])
    application.listen(config.v.server.port)
    print("Starting server on port %s" % config.v.server.port)

    io_loop = tornado.ioloop.IOLoop.current()

    LoveServer.instance().main_thread = io_loop

    io_loop.start()
