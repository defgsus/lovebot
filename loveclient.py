import time

import tornado.websocket

from lovelib.client import LoveClient

#conn = yield tornado.websocket.websocket_connect(
#    "ws://127.0.0.1:8001/ws",
#)

client = LoveClient("ws://127.0.0.1:8001/ws")
client.mainloop()


