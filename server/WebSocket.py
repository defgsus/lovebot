import tornado.websocket


class WebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened: %s" % self.request)
        self.write_message("Welcome to server")

    def on_message(self, message):
        print("msg: %s" % message)
        self.write_message("You said: " + message)

    def on_close(self):
        print("WebSocket closed")

