import time
import json
import random

import tornado.websocket
import tornado.ioloop

from .api import LoveApi
from .LoveBot import LoveBot
from .LoveWorld import LoveWorld


class LoveClient(object):

    def __init__(self, url):
        self.connection = None
        self.api = LoveApi(self.send_command)
        self._world = None
        self._world_interface = None
        self._bots = None
        self._bot_interfaces = {}
        self._initialized = False
        self._last_on_idle = None
        self._last_update = None
        self.time = 0.
        self.UPDATE_DELAY = 1.
        self.IDLE_DELAY = 1.

        future = tornado.websocket.websocket_connect(
            url=url,
            callback=self._on_connect,
            on_message_callback=self._on_message,
        )
        future.add_done_callback(self._on_connect)

    @property
    def world(self):
        return self._world_interface

    def _on_connect(self, f):
        self.connection = f.result()
        self.api.get_world()
        self.api.get_bots()

    def _on_message(self, msg):
        #print("msg", msg)
        try:
            data = json.loads(msg)
            self.time = max(self.time, data["ts"])
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
        self.on_event(event, data)

    def _on_world(self, world):
        self._world = world
        self._world_interface = LoveWorld.from_json(self, self._world)
        if not self._initialized and self._world and self._bots:
            self._initialized = True
            self.on_connect()

    def _on_bots(self, bots):
        self._bots = bots
        for bot in self._bots:
            if bot["id"] in self._bot_interfaces:
                boti = self._bot_interfaces[bot["id"]]
                boti.is_connected = True
                boti.update_from_json(bot)

        if not self._initialized and self._world and self._bots:
            self._initialized = True
            self.on_connect()

        tornado.ioloop.IOLoop.current().call_later(
            self.UPDATE_DELAY, self.api.get_bots
        )

        cur_time = time.time()
        if self._last_update is None:
            self._last_update = cur_time - 1
        self.on_update(cur_time - self._last_update)
        self._last_update = cur_time

    def _write_message(self, msg):
        self.connection.write_message(msg)

    def _write_json(self, data):
        msg = json.dumps(data)
        self._write_message(msg)

    def _random_bot_id(self):
        return "".join(chr(random.randint(ord('A'),ord('Z'))) for i in range(7))

    def _on_idle(self):
        cur_time = time.time()
        if self._last_on_idle is None:
            self._last_on_idle = cur_time - 1
        self.on_idle(cur_time - self._last_on_idle)
        self._last_on_idle = cur_time

        tornado.ioloop.IOLoop.instance().call_later(self.IDLE_DELAY, self._on_idle)

    ##### public api ######

    def mainloop(self):
        tornado.ioloop.IOLoop.instance().add_callback(self._on_idle)
        return tornado.ioloop.IOLoop.instance().start()

    def send_command(self, name, **kwargs):
        if kwargs:
            self._write_json({"cmd": name, "args": kwargs})
        else:
            self._write_json({"cmd": name})

    def get_bot(self, bot_id):
        if bot_id not in self._bot_interfaces:
            self._bot_interfaces[bot_id] = LoveBot(self, bot_id)
        return self._bot_interfaces[bot_id]

    def create_bot(self, bot_id=None, name=None):
        if not bot_id:
            bot_id = self._random_bot_id()
        if bot_id in self._bot_interfaces:
            raise KeyError("duplicate bot_id '%s'" % bot_id)
        bot = LoveBot(self, bot_id=bot_id)
        self._bot_interfaces[bot_id] = bot
        self.api.create_bot(bot_id, name)
        self.api.get_bots()
        return bot

    #### overload these ####

    def on_connect(self):
        pass

    def on_event(self, name, data):
        pass

    def on_update(self, dt):
        pass

    def on_idle(self, dt):
        pass