import json
import tornado.websocket

from lovelib.server import LoveServer


class WebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = LoveServer().instance()
        self.is_open = False

    def timestamp(self):
        return self.server.world.sim_time

    def open(self):
        print("WS OPEN", self)
        if not self.server.add_connection(self):
            self.close()
        else:
            self.is_open = True

    def on_close(self):
        print("WS CLOSE", self)
        self.is_open = False
        self.server.remove_connection(self)

    def on_message(self, message):
        #print("msg: %s" % message)
        try:
            data = json.loads(message)
            cmd = data.get("cmd")
            if not cmd:
                self.error_response("No 'cmd'")
            else:
                self.server.on_command(self, data["cmd"], data.get("args"))
        except ValueError:
            self.error_response("Invalid json")

    def write_message_json(self, data):
        if self.is_open:
            data["ts"] = self.timestamp()
            self.write_message(json.dumps(data))

    def error_response(self, error_str):
        if self.is_open:
            self.write_message_json({"error": str(error_str)})
