import json

import tornado.websocket
import tornado.ioloop

from .api import LoveApi


class LoveClient(object):

    def __init__(self, url):
        self.connection = None
        self.api = LoveApi(self.send_command)
        self._world = None
        self._bots = None
        self._initialized = False

        future = tornado.websocket.websocket_connect(
            url=url,
            callback=self._on_connect,
            on_message_callback=self._on_message,
        )
        future.add_done_callback(self._on_connect)

    def _on_connect(self, f):
        self.connection = f.result()
        self.api.get_world()
        self.api.get_bots()

    def _on_message(self, msg):
        print("msg", msg)
        try:
            data = json.loads(msg)
        except (TypeError, ValueError):
            print("illegal message '%s'" % msg)
            return
        if "event" in data:
            self._on_event(data["event"]["name"], data["event"].get("data", {}))
        if "world" in data:
            self._on_world(data["world"])
        if "bots" in data:
            self._on_bots(data["bots"])

    def _on_event(self, event, data):
        pass

    def _on_world(self, world):
        self._world = world
        if not self._initialized and self._world and self._bots:
            self._initialized = True
            self.on_connect()

    def _on_bots(self, bots):
        self._bots = bots
        if not self._initialized and self._world and self._bots:
            self._initialized = True
            self.on_connect()

    def _write_message(self, msg):
        self.connection.write_message(msg)

    def _write_json(self, data):
        msg = json.dumps(data)
        self._write_message(msg)

    ##### public api ######

    def mainloop(self):
        return tornado.ioloop.IOLoop.instance().start()

    def send_command(self, name, **kwargs):
        if kwargs:
            self._write_json({"cmd": name, "args": kwargs})
        else:
            self._write_json({"cmd": name})

    def create_bot(self, bot_id, name=None):
        self.api.create_bot(bot_id, name)

    #### overload these ####

    def on_connect(self):
        pass

    def on_event(self, event, data):
        pass
