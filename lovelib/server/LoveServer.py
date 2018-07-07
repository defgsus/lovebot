from ..sim.World import *


class LoveServer(object):

    _instance = None

    def __init__(self):
        self.world = World()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = LoveServer()
        return cls._instance

    def on_message(self, msg):
        command = msg.get("command")
        if command:
            self.on_command(command)

    def on_command(self, msg):
        if isinstance(msg, str):
            pass