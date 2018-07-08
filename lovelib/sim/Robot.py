import random

from .force import *


class Wheel(PointWithForce):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 0.


class Robot:

    def __init__(self, bot_id, world, heading=None, name=None):
        self.bot_id = bot_id
        self.world = world
        self.radius = 1.
        self.name = name or str(bot_id)
        if heading is None:
            heading = random.uniform(0, 7)
        si, ca = math.sin(heading), math.cos(heading)
        self.l_wheel = Wheel(-self.radius * si, -self.radius * ca)
        self.r_wheel = Wheel( self.radius * si,  self.radius * ca)
        self.wheels = (self.l_wheel, self.r_wheel)
        self.prev_c = []

    def center(self):
        return (self.l_wheel.x + self.r_wheel.x) / 2., \
               (self.l_wheel.y + self.r_wheel.y) / 2.

    def prev_center(self):
        return self.prev_c[0][1] if self.prev_c else self.center()

    def heading(self):
        return math.atan2(self.l_wheel.y - self.r_wheel.y,
                        -(self.l_wheel.x - self.r_wheel.x))

    def velocity(self):
        return (self.l_wheel.x_vel + self.r_wheel.x_vel) * .5, \
               (self.l_wheel.y_vel + self.r_wheel.y_vel) * .5,

    def to_json(self):
        return {
            "world_id": self.world.world_id,
            "id": self.bot_id,
            "name": self.name,
            "radius": self.radius,
            "center": self.center(),
            "p_center": self.prev_center(),
            "heading": self.heading(),
            "wheel_speed": [self.l_wheel.speed, self.r_wheel.speed],
        }

    def set_wheel_speed(self, left, right):
        self.l_wheel.speed = left
        self.r_wheel.speed = right

    def add_force(self, x, y):
        for w in self.wheels:
            w.x_vel += x
            w.y_vel += y

    def move(self, dt, iter=1):
        a = self.heading()
        si, co = math.sin(a), math.cos(a)
        for it in range(iter):

            # bot/world collision
            self._bot_world_collision(dt)

            # velocity from wheel-speed
            for w in self.wheels:
                if w.speed:
                    w.x_vel += si * w.speed * dt
                    w.y_vel += co * w.speed * dt
                w.apply_force(dt)

            # keep wheels "together"
            x_vel, y_vel = solve_distance_constraint(
                self.l_wheel.x, self.l_wheel.y,
                self.r_wheel.x, self.r_wheel.y,
                self.radius*2.)
            self.l_wheel.x_vel += x_vel * dt
            self.l_wheel.y_vel += y_vel * dt
            self.r_wheel.x_vel -= x_vel * dt
            self.r_wheel.y_vel -= y_vel * dt

            # wheel with world collision
            for w in self.wheels:
                x_vel, y_vel = collide_sphere_with_distancefield(
                    w.x, w.y, 0.01, w.x_vel, w.y_vel, self.world.df)
                w.x_vel += x_vel * dt
                w.y_vel += y_vel * dt
                w.apply_force(dt)

        # store position history
        self.prev_c.append((self.world.sim_time, self.center()))
        if self.prev_c[0][0] < self.world.sim_time - 1:
            del self.prev_c[0]

    def _bot_world_collision(self, dt):
        center_x, center_y = self.center()
        vel_x, vel_y = self.velocity()

        vel_x, vel_y = collide_sphere_with_distancefield(
            center_x, center_y, self.radius, vel_x, vel_y, self.world.df)

        self.add_force(vel_x*dt, vel_y*dt)
