import tornado.websocket


class LoveClient(object):

    def __init__(self, url):
        self._future = tornado.websocket.websocket_connect(
            url=url,
            on_message_callback=self._on_message,
        )
        self._future.add_done_callback(self._on_connect)

    def _on_connect(self, f):
        print("connect")
        print(f)

    def _on_message(self, msg):
        print("client._on_message", msg)

    def write_message(self, msg):
        pass#self.ws.write_message(msg)
