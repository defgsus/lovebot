from .math import *


class BoundingBox:
    def __init__(self, min_x=0, max_x=0, min_y=0, max_y=0):
        self.min_x, self.max_x, self.min_y, self.max_y = min_x, min_y, max_x, max_y

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y

    def unite(self, box):
        self.min_x = min(self.min_x, box.min_x)
        self.min_y = min(self.min_y, box.min_y)
        self.max_x = max(self.max_x, box.max_x)
        self.max_y = max(self.max_y, box.max_y)
        return self

    def united(self, box):
        return BoundingBox(
            min(self.min_x, box.min_x),
            min(self.min_y, box.min_y),
            max(self.max_x, box.max_x),
            max(self.max_y, box.max_y)
        )

    def adjust(self, x1, y1, x2, y2):
        self.min_x += x1
        self.min_y += y1
        self.max_x += x2
        self.max_y += y2
        return self

    def to_json(self):
        return {
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }


class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(%s, %s, %s, %s)" % (self.x, self.y, self.x_vel, self.y_vel)

    def distance_to(self, x, y):
        dx, dy = x - self.x, y - self.y
        return math.sqrt(dx*dx + dy*dy)
    
    def bounding_box(self):
        return BoundingBox(self.x, self.y, self.x, self.y)

    def to_json(self):
        return {
            "type": "point",
            "x": self.x,
            "y": self.y,
        }


class Circle(Point):
    def __init__(self, x, y, radius, inverted=False):
        super().__init__(x, y)
        self.radius = radius
        self.inverted = inverted

    def distance_to(self, x, y):
        dx, dy = x - self.x, y - self.y
        d = math.sqrt(dx*dx + dy*dy) - self.radius
        return -d if self.inverted else d

    def bounding_box(self):
        return BoundingBox(self.x-self.radius, self.y-self.radius,
                           self.x+self.radius, self.y+self.radius)

    def to_json(self):
        return {
            "type": "circle",
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "inverted": self.inverted,
        }


class Rectangle(Point):
    def __init__(self, x1, y1, x2, y2, inverted=False):
        super().__init__(x1, y1)
        self.x2 = x2
        self.y2 = y2
        self.inverted = inverted

    @property
    def width(self): return self.x2 - self.x
    @property
    def height(self): return self.y2 - self.y
    @property
    def center_x(self): return (self.x + self.x2) / 2.
    @property
    def center_y(self): return (self.y + self.y2) / 2.

    def distance_to(self, x, y):
        dx, dy = abs(x-self.center_x) - self.width/2., abs(y-self.center_y) - self.height/2.
        d1, d2 = max(dx, 0), max(dy, 0)
        d = min(max(dx, dy), 0.0) + math.sqrt(d1*d1+d2*d2)
        return -d if self.inverted else d

    def bounding_box(self):
        return BoundingBox(self.x, self.y, self.x2, self.y2)

    def to_json(self):
        return {
            "type": "rectangle",
            "x1": self.x,
            "y1": self.y,
            "x2": self.x2,
            "y2": self.y2,
            "inverted": self.inverted,
        }


class CenteredRectangle(Point):
    def __init__(self, x, y, width, height, inverted=False):
        super().__init__(x, y)
        self.width, self.height = width, height
        self.inverted = inverted

    def distance_to(self, x, y):
        dx, dy = abs(x-self.x) - self.width, abs(y-self.y) - self.height
        d1, d2 = max(dx, 0), max(dy, 0)
        d = min(max(dx, dy), 0.0) + math.sqrt(d1*d1+d2*d2)
        return -d if self.inverted else d

    def bounding_box(self):
        w, h = self.width, self.height
        return BoundingBox(self.x-w, self.y-h, self.x+w, self.y+h)

    def to_json(self):
        return {
            "type": "centered_rectangle",
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "inverted": self.inverted,
        }