from functools import partial

from lovelib.sim import DistanceField
from lovelib.sim.math import distance


class LoveWorld:

    def __init__(self, client, world_id, df_data):
        self.client = client
        self.world_id = world_id
        self.df = DistanceField.from_json(df_data)

    @classmethod
    def from_json(cls, client, data):
        world = cls(client, data["world_id"], data["df"])
        return world

    @property
    def time(self):
        return self.client.time

    def distance_to(self, x, y, exclude_bot_ids=None):
        """Returns the distance between x,y and the closest surface in the world"""
        exclude_bot_ids = exclude_bot_ids or []
        d = self.df.distance_to(x, y)
        for bot in self.client._bots:
            if bot["id"] not in exclude_bot_ids:
                d = min(d, distance(x, y, bot["center"][0], bot["center"][1]) - bot["radius"])
        return d

    def trace(self, x, y, nx, ny, max_steps=None, exclude_bot_ids=None):
        return self.df.trace(
            x, y, nx, ny, max_steps=max_steps,
            dist_func=partial(self.distance_to, exclude_bot_ids=exclude_bot_ids)
        )
