import time
import json
import random

import tornado.websocket
import tornado.ioloop

from .api import LoveApi
from .LoveBot import LoveBot
from .LoveWorld import LoveWorld


class LoveClient(object):

    def __init__(self, url=None, username=None, password=None, config=None):
        self.config = config
        self.connection = None
        self.api = LoveApi(self.send_command)
        self._world = None
        self._world_interface = None
        self._bots = None
        self._bot_interfaces = {}
        self._initialized = False
        self._last_on_idle = None
        self._last_update = None
        self._username = username
        self._password = password
        self._is_login = False
        self.time = 0.
        self.UPDATE_DELAY = 1.
        self.IDLE_DELAY = 1.

        if self.config is not None:
            url = "%s:%s" % (self.config.host, self.config.port)
            self._username = config.user
            self._password = config.password

        url = "ws://%s/ws" % url
        print("connecting to %s" % url)
        future = tornado.websocket.websocket_connect(
            url=url,
            callback=self._on_connect,
            on_message_callback=self._on_message,
        )

    @property
    def world(self):
        return self._world_interface

    def _on_connect(self, f):
        self.connection = f.result()
        print("connected")
        self.api.get_world()
        self.api.get_bots()
        if self._username and self._password:
            self.api.login(self._username, self._password)

    def _on_message(self, msg):
        if msg is None:
            print("connection closed")
            exit(-1)
        #print("msg", msg)
        try:
            data = json.loads(msg)
            self.time = max(self.time, data["ts"])
        except (TypeError, ValueError):
            print("illegal message '%s'" % msg)
            return
        if "error" in data:
            self._on_error(data["error"])
        if "event" in data:
            self._on_event(data["event"]["name"], data["event"].get("data", {}))
        if "world" in data:
            self._on_world(data["world"])
        if "bots" in data:
            self._on_bots(data["bots"])

    def _on_event(self, event, data):
        if event == "login" and data["user"] == self._username:
            self._is_login = True
            self._call_update_if_ready()
        self.on_event(event, data)

    def _on_error(self, error):
        print("error:", error)
        self.on_error(error)

    def _on_world(self, world):
        self._world = world
        self._world_interface = LoveWorld.from_json(self, self._world)

        self._call_update_if_ready()

    def _on_bots(self, bots):
        self._bots = bots
        for bot in self._bots:
            if bot["id"] in self._bot_interfaces:
                boti = self._bot_interfaces[bot["id"]]
                boti.is_connected = True
                boti.update_from_json(bot)

        self._call_update_if_ready()

        tornado.ioloop.IOLoop.current().call_later(
            self.UPDATE_DELAY, self.api.get_bots
        )

    def _call_update_if_ready(self):
        ready = self._world and self._bots is not None
        ready &= not (self._username and self._password) or self._is_login
        if not ready:
            return

        if not self._initialized:
            self._initialized = True
            self.on_connect()

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
        while True:
            bot_id = "".join(chr(random.randint(ord('A'),ord('Z'))) for i in range(7))
            if not self._bots or bot_id not in self._bots:
                return bot_id

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

    def send_command(self, _cmd_name, **kwargs):
        #print("send", _cmd_name, kwargs)
        if kwargs:
            self._write_json({"cmd": _cmd_name, "args": kwargs})
        else:
            self._write_json({"cmd": _cmd_name})

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

    def on_error(self, error):
        pass

    def on_event(self, name, data):
        pass

    def on_update(self, dt):
        pass

    def on_idle(self, dt):
        pass
