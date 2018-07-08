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
        self.connections[ip] = {
            "con": con,
            "id": str(id(con)),
            "ip": ip,
            "event_count": -1,
        }
        return True

    def remove_connection(self, con):
        ip = con.request.remote_ip
        if ip in self.connections:
            del self.connections[ip]

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

    def on_command(self, con, cmd):
        if isinstance(cmd, str):
            cmd = {"name": cmd}
        if "name" not in cmd:
            con.error_response("No 'name' in 'cmd'")
        name = cmd["name"]
        args = cmd.get("args", {})

        if name == "get_world":
            self.send(con, "world", self.world.to_json())
        elif name == "get_connections":
            self.send(con, "connections", self.connections_json())
        elif name == "get_bots":
            self.send(con, "bots", self.bots_json())
        elif name == "create_bot":
            name = args.get("name", self.get_random_bot_name())
            bot = self.world.create_new_bot(name=name)

    def simulation_mainloop(self):
        last_time = time.time()
        while True:
            cur_time = time.time()
            delta_time = cur_time - last_time
            self.world.step(delta_time)
            last_time = cur_time

            self.send_events()

            time.sleep(1./30.)

    def send(self, con, topic, data):
        con.write_message_json({topic: data})

    def send_events(self):
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