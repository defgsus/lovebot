import random
import math

from lovelib.client import LoveClient


class MyLoveClient(LoveClient):

    def on_connect(self):
        self.bot = self.create_bot()

    def on_event(self, name, data):
        pass

    def on_update(self, dt):
        if not self.bot.is_connected:
            return

        max_speed = 3
        seek_distance = 6. + 5. * math.sin(self.time / 5.)
        bot = self.bot

        # get stereo distance to wall ahead
        tl = bot.trace_heading_degree(-20)
        tr = bot.trace_heading_degree(20)

        if 1:
            print("{}: target-dist={:.2f}, trace=[{:.2f}, {:.2f}], speed=[{:.2f}, {:.2f}], dir=[{:.2f}, {:.2f}]".format(
                bot.name,
                seek_distance,
                tl, tr,
                bot.speed_left, bot.speed_right,
                bot.nx, bot.ny,
            ))

        # set wheel speed to match distance
        bot.set_wheel_speed(
            min(max_speed,max(-max_speed, tl-seek_distance)),
            min(max_speed,max(-max_speed, tr-seek_distance)),
        )


if __name__ == "__main__":
    client = MyLoveClient("127.0.0.1:8001", "admin", "admin")
    client.mainloop()


