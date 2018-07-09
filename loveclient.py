import time

import tornado.websocket

from lovelib.client import LoveClient


class MyLoveClient(LoveClient):

    def on_connect(self):
        pass

    def on_event(self, name, data):
        print("event", name, data)
        if name == "bot_created":
            print(self.bot)

    def on_update(self, dt):
        if not hasattr(self, "bot"):
            self.bot = self.create_bot()
            self.bot.set_wheel_speed(.1, .2)

        tl = self.bot.trace_heading(-.1)
        tr = self.bot.trace_heading(.1)
        print(dt, round(tl, 2), round(tr, 2), self.bot)
        self.bot.set_wheel_speed(
            min(1,max(-1, tl-10)),
            min(1,max(-1, tr-10)),
        )



client = MyLoveClient("ws://127.0.0.1:8001/ws")
client.mainloop()


