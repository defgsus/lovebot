from .math import *
from .csg import Point, Circle


class ForceMixin:
    def __init__(self):
        self.x_vel = 0
        self.y_vel = 0

    def apply_force(self, dt):
        self.x += dt * self.x_vel
        self.y += dt * self.y_vel
        self.x_vel -= dt * self.x_vel
        self.y_vel -= dt * self.y_vel
        if abs(self.x_vel) <= EPSILON:
            self.x_vel = 0.
        if abs(self.y_vel) <= EPSILON:
            self.y_vel = 0.


class PointWithForce(Point, ForceMixin):
    pass


class CircleWithForce(Circle, ForceMixin):
    pass


