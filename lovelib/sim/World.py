from .DistanceField import *
from .csg import *
from .Robot import *


class World:
    def __init__(self):
        self.world_id = "WORLD"
        self.sim_time = 0
        self.bots = {}
        self.df = DistanceField()

        self.df.add(Rectangle(7, 2, 5, 9))
        self.df.add(Rectangle(0, 0, 15, 15, True))
        self.df.add(Circle(-4, -5, 3))

        self._id = 0

    def new_bot_id(self):
        self._id += 1
        return "BOT%s" % self._id

    def new_bot(self):
        b = Robot(bot_id=self.new_bot_id(), world=self)
        self.bots[b.bot_id] = b
        return b

    def remove_bot(self, bot_or_id):
        bot_id = bot_or_id.bot_id if isinstance(bot_or_id, Robot) else bot_or_id
        if bot_id in self.bots:
            self.bots.pop(bot_id)

    def step(self, dt):
        for b in self.bots.values():
            b.move(dt)

        self.sim_time += dt

    def render_pygame(self, screen):
        screen.fill((0,0,0))
        for y in range(-16,16):
            for x in range(-16,16):
                d = self.df.distance_to(x, y)
                if d <= 0.01:
                    screen.set_at((int(x*10+160), int(160-y*10)), (255,0,0))
        for r in self.bots.values():
            for w in r.wheels:
                screen.set_at((int(w.point.x*10+160), int(160-w.point.y*10)), (255,255,255))

    def state(self):
        """Complete state object"""
        return {
            "world_id": self.world_id,
            "time": self.sim_time,
            "bots": {r.bot_id: r.state() for r in self.bots.values()},
            "rects": self.df.objects,
            "circles": self.df.objects,
        }


