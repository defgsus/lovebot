from lovelib.sim import DistanceField


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

