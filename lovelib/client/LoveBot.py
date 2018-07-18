import math


class LoveBot(object):

    def __init__(self, client, bot_id):
        self.client = client
        self.bot_id = bot_id
        self.name = ""
        self.is_connected = False
        self.radius = 0.
        self.x = 0.
        self.y = 0.
        self.nx = 0.
        self.ny = 1.
        self.vx = 0.
        self.vy = 0.
        self.speed_left = 0.
        self.speed_right = 0.
        self.heading = 0.

    def __str__(self):
        return "LoveBot(id='%s', name='%s', pos=[%s, %s], dir=[%s, %s], vel=[%s, %s], wheels=[%s, %s])" % (
            self.bot_id, self.name, round(self.x, 2), round(self.y, 2),
            round(self.nx, 2), round(self.ny, 2),
            round(self.vx, 2), round(self.vy, 2),
            round(self.speed_left, 2), round(self.speed_right, 2),
        )
    
    def update_from_json(self, data):
        self.name = data["name"]
        self.x, self.y = data["center"]
        self.vx = self.x - data["p_center"][0]
        self.vy = self.y - data["p_center"][1]
        self.speed_left, self.speed_right = data["wheel_speed"]
        self.heading = data["heading"]
        self.radius = data["radius"]
        self.nx, self.ny = math.sin(self.heading), math.cos(self.heading)

    @property
    def direction(self):
        return self.nx, self.ny

    @property
    def velocity(self):
        return self.vx, self.vy

    def set_wheel_speed(self, left, right):
        self.client.api.set_wheel_speed(self.bot_id, left, right)

    def trace_front(self, max_steps=None):
        return self.client.world.trace(
            self.x + self.radius * self.nx,
            self.y + self.radius * self.ny,
            self.nx, self.ny,
            max_steps=max_steps,
            exclude_bot_ids=[self.bot_id],
        )

    def trace_radians(self, radians, max_steps=None):
        nx, ny = math.sin(self.heading + radians), math.cos(self.heading + radians)
        return self.client.world.trace(
            self.x + self.radius * nx,
            self.y + self.radius * ny,
            nx, ny,
            max_steps=max_steps,
            exclude_bot_ids=[self.bot_id],
        )

    def trace_degree(self, degree, max_steps=None):
        return self.trace_radians(degree / 180. * math.pi, max_steps)

    def trace_left(self, max_steps=None):
        return self.trace_degree(90, max_steps=max_steps)

    def trace_right(self, max_steps=None):
        return self.trace_degree(-90, max_steps=max_steps)

    def trace_back(self, max_steps=None):
        return self.trace_degree(180, max_steps=max_steps)