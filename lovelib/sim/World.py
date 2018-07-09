from ..util import Configuration
from .DistanceField import *
from .csg import *
from .Robot import *


class World:
    def __init__(self, config):
        self.config_world = (config or Configuration.default_configuration()).v.world
        self.world_id = "WORLD"
        self.sim_time = 0
        self.bots = {}
        self.event_stack = []
        self._event_count = 0
        self._bot_count = 0

        self.df = DistanceField()

        self.df.add(Rectangle(0, 0, 15, 15, True))
        self.df.add(Rectangle(7, 2, 5, 9))  # 2, -7
        self.df.add(Rectangle(-4, -4, 6, 3))
        self.df.add(Circle(-4, 5, 3))

        #self.create_new_bot(name="Albert").set_wheel_speed(.5, .9)
        #self.create_new_bot(name="Sigmund").set_wheel_speed(1.3, .8)
        #self.create_new_bot(name="Eragon").set_wheel_speed(1.5, 1.8)

    def set_config(self, config=None):
        self.config_world = (config or Configuration.default_configuration()).v.world

    def create_new_bot_id(self):
        self._bot_count += 1
        return "B%s" % self._bot_count

    def create_new_bot(self, **kwargs):
        # find position
        bbox = self.df.bounding_box()
        radius = 1.
        count = 0
        while True:
            x = random.uniform(bbox.min_x+radius, bbox.max_x-radius)
            y = random.uniform(bbox.min_y+radius, bbox.max_y-radius)
            if self.df.distance_to(x, y) > radius:
                break
            count += 1
            if count > 10000:
                raise RecursionError("Can't find start position for bot %s" % kwargs)

        # find bot_id
        if "bot_id" in kwargs:
            bot_id = kwargs.pop("bot_id")
            if bot_id in self.bots:
                raise KeyError("duplicate bot_id '%s'" % bot_id)
        else:
            bot_id = self.create_new_bot_id()

        # create
        b = Robot(x=x, y=y, radius=radius, bot_id=bot_id, world=self, **kwargs)
        self.bots[b.bot_id] = b
        self.add_event("bot_created", id=b.bot_id, name=b.name)
        return b

    def remove_bot(self, bot_or_id):
        bot_id = bot_or_id.bot_id if isinstance(bot_or_id, Robot) else bot_or_id
        if bot_id in self.bots:
            self.bots.pop(bot_id)
            self.add_event("bot_removed", bot_id=bot_id)

    def step(self, dt):
        for b in self.bots.values():
            b.max_speed = self.config_world.max_speed
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
            "ts": self.sim_time,
            "df": self.df.to_json(),
        }


