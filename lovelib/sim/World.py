from .DistanceField import *
from .csg import *
from .Robot import *


class World:
    def __init__(self):
        self.world_id = "WORLD"
        self.sim_time = 0
        self.bots = {}
        self.event_stack = []
        self._event_count = 0
        self._bot_count = 0

        self.df = DistanceField()

        self.df.add(Rectangle(0, 0, 15, 15, True))
        self.df.add(Rectangle(7, 2, 5, 9))
        self.df.add(Circle(-4, -5, 3))

    def create_new_bot_id(self):
        self._bot_count += 1
        return "B%s" % self._bot_count

    def create_new_bot(self, **kwargs):
        b = Robot(bot_id=self.create_new_bot_id(), world=self, **kwargs)
        self.bots[b.bot_id] = b
        self.add_event("bot_created", id=b.bot_id, name=b.name)
        return b

    def remove_bot(self, bot_or_id):
        bot_id = bot_or_id.bot_id if isinstance(bot_or_id, Robot) else bot_or_id
        if bot_id in self.bots:
            self.bots.pop(bot_id)

    def step(self, dt):
        for b in self.bots.values():
            b.move(dt)

        self.sim_time += dt

    def add_event(self, event_name, **kwargs):
        event = {
            "name": event_name,
            "ts": self.sim_time,
            "data": kwargs,
        }
        self._event_count += 1
        self.event_stack.append((self._event_count, event))

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

    def to_json(self):
        """World to json"""
        return {
            "world_id": self.world_id,
            "time": self.sim_time,
            "df": self.df.to_json(),
        }


