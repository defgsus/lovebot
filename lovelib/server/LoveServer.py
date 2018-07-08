import threading
import time
import functools
import datetime

import tornado.ioloop

from ..sim.World import *


class LoveServer(object):

    _instance = None

    def __init__(self):
        self.world = World()
        self.connections = dict()
        self.main_thread = None
        self.thread = threading.Thread(target=self.simulation_mainloop)
        self.thread.start()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = LoveServer()
        return cls._instance

    def add_connection(self, con):
        ip = con.request.remote_ip
        if ip in self.connections:
            con.error_response("IP %s already connected" % ip)
            return False
        new_con = {
            "con": con,
            "id": str(id(con)),
            "ip": ip,
            "event_count": -1,
        }
        self.connections[ip] = new_con
        self.send_event("connection_opened", id=new_con["id"])
        return True

    def remove_connection(self, con):
        ip = con.request.remote_ip
        if ip in self.connections:
            self.send_event("connection_closed", id=self.connections[ip]["id"])
            del self.connections[ip]

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

        if name == "get_world":
            self.send(con, "world", self.world.to_json())

        elif name == "get_connections":
            self.send(con, "connections", self.connections_json())

        elif name == "get_bots":
            self.send(con, "bots", self.bots_json())

        elif name == "create_bot":
            name = args.get("name", self.get_random_bot_name())
            self.world.create_new_bot(name=name)

        elif name == "set_wheel_speed":
            bot_id = args.get("bot_id", "")
            if bot_id not in self.world.bots:
                con.error_response("unknown bot_id '%s'" % bot_id)
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