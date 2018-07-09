import threading
import time
import functools
import datetime

import tornado.ioloop

from ..sim.World import *
from ..util import Configuration


class LoveServer(object):

    _instance = None

    def __init__(self, config=None):
        config = config or Configuration.default_configuration()
        self.config = config.v
        self.world = World(config)
        self.connections = dict()
        self.main_thread = None
        self.thread = threading.Thread(target=self.simulation_mainloop)
        self.thread.start()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = LoveServer()
        return cls._instance

    def set_config(self, config=None):
        config = config or Configuration.default_configuration()
        self.config = config.v
        self.world.set_config(config)

    def add_connection(self, con):
        con_id = str(id(con))
        if con_id in self.connections:
            con.error_response("'%s' is already connected" % con_id)
            return False
        if len(self.connections) >= self.config.server.max_connections:
            con.error_response("maximum connections reached")
            return False
        new_con = {
            "con": con,
            "id": con_id,
            "ip": con.request.remote_ip,
            "user": None,
            "event_count": -1,
            "bots": [],
        }
        self.connections[con_id] = new_con
        self.send_event("connection_opened", id=new_con["id"])
        return True

    def remove_connection(self, con):
        con_id = str(id(con))
        if con_id in self.connections:
            for bot in self.connections[con_id]["bots"]:
                # TODO: threading issue
                self.world.remove_bot(bot)
            del self.connections[con_id]

        self.send_event("connection_closed", id=con_id)

    def connection_props(self, con_or_id):
        if con_or_id in self.connections:
            return self.connections[con_or_id]
        con_id = str(id(con_or_id))
        if con_id in self.connections:
            return self.connections[con_id]
        raise KeyError("unknown connection '%s'" % con_or_id)

    def send_event(self, event_name, **kwargs):
        """Send to all connections"""
        for con in self.connections.values():
            self.send(
                con["con"],
                "event",
                {"ts": self.world.sim_time, "name": event_name, "data": kwargs}
            )

    def connections_json(self):
        return [
            {"id": c["id"], "ip": c["ip"]}
            for c in self.connections.values()
        ]

    def bots_json(self):
        return [
            b.to_json()
            for b in self.world.bots.values()
        ]

    def on_command(self, con, cmd, args=None):
        if isinstance(cmd, str):
            cmd = {"name": cmd}
        name = cmd.get("name")
        if not "name":
            con.error_response("No 'name' in 'cmd'")
            return False
        args = args or {}

        props = self.connection_props(con)
        logged_in = props["logged_in"]

        if not logged_in and name not in ("get_world", "get_connections", "get_bots", "login"):
            con.error_response("No access")
            return False

        # print("CMD", time.time(), cmd, args)

        if name == "get_world":
            self.send(con, "world", self.world.to_json())

        elif name == "get_connections":
            self.send(con, "connections", self.connections_json())

        elif name == "get_bots":
            self.send(con, "bots", self.bots_json())

        elif name == "login":
            return self._login(con, args.get("name"), args.get("pw"))

        elif name == "logout":
            self._logout(con)

        elif name == "create_bot":
            name = args.get("name") or self.get_random_bot_name()
            bot_id = args.get("bot_id")
            return self._create_bot(con, bot_id, name)

        elif name == "set_wheel_speed":
            bot_id = args.get("bot_id", "")
            if bot_id not in self.world.bots:
                con.error_response("unknown bot_id '%s'" % bot_id)
                return False
            else:
                bot = self.world.bots[bot_id]
                sleft, sright = args.get("left"), args.get("right")
                if not isinstance(sleft, (float, int)):
                    sleft = bot.l_wheel.speed
                if not isinstance(sright, (float, int)):
                    sright = bot.r_wheel.speed
                bot.set_wheel_speed(sleft, sright)
        else:
            con.error_response("unknown command '%s'" % name)
            return False
        return True

    def _create_bot(self, con, bot_id=None, name=None):
        kwargs = {"name": name}
        if bot_id:
            if bot_id in self.world.bots:
                con.error_response("duplicate bot_id '%s'" % bot_id)
                return False
            else:
                kwargs["bot_id"] = bot_id
        props = self.connection_props(con)
        if len(self.world.bots) >= self.config.world.max_bots:
            con.error_response(
                "reached max number of bots (%s)" % self.config.world.max_bots)
            return False
        if len(props["bots"]) >= self.config.world.max_bots_per_user:
            con.error_response(
                "reached max number of bots per user (%s)" % self.config.world.max_bots_per_user)
            return False
        bot = self.world.create_new_bot(**kwargs)
        props["bots"].append(bot)
        return True

    def _login(self, con, user, pw):
        props = self.connection_props(con)
        if props["user"]:
            self._logout(con)
        valid = False
        for u, p in (("bergi", "u-und-p")):
            if u == user and p == pw:
                valid = True
                break
        if not valid:
            con.error_response("Invalid user or password")
            return False
        props["user"] = user

    def _logout(self, con):
        props = self.connection_props(con)
        if props["user"]:
            self.send_event("logged_out", user=props["user"])
        props["user"] = None

    def simulation_mainloop(self):
        last_time = time.time()
        while True:
            cur_time = time.time()
            delta_time = cur_time - last_time
            self.world.step(delta_time)
            last_time = cur_time

            self.queue_world_events()

            time.sleep(1./30.)

    def send(self, con, topic, data):
        con.write_message_json({topic: data})

    def queue_world_events(self):
        send_events = []
        while self.world.event_stack:
            event_count, event_data = self.world.event_stack.pop(0)
            for con in self.connections.values():
                if con["event_count"] < event_count:
                    send_events.append((con["con"], "event", event_data))
                con["event_count"] = event_count
        if send_events:
            def _send_them(events):
                for args in events:
                    self.send(*args)

            self.main_thread.add_callback(functools.partial(_send_them, send_events))

    def get_random_bot_name(self):
        NAMES = ["Sebastian", "David", "Cordula", "Ingrid"]
        return NAMES[random.randrange(len(NAMES))]