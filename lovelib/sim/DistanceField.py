from .csg import *


class DistanceField:
    def __init__(self):
        self.objects = []
        self.FUDGE = 1.
        self.MAX_DISTANCE = 10000.
        self.MIN_SURFACE = 0.001
        self.MAX_STEPS = 100

    def bounding_box(self):
        bb = BoundingBox()
        for o in self.objects:
            bb.unite(o.bounding_box())
        return bb

    def add(self, obj):
        self.objects.append(obj)

    def distance_to(self, x, y):
        d = self.MAX_DISTANCE
        for obj in self.objects:
            d = min(d, obj.distance_to(x, y))
        return d

    def normal(self, x, y, e=0.02):
        dx = self.distance_to(x + e, y) - self.distance_to(x - e, y)
        dy = self.distance_to(x, y + e) - self.distance_to(x, y - e)
        d = dx*dx+dy*dy
        if not d:
            return 0., 0.
        d = math.sqrt(d)
        return dx / d, dy / d

    def trace(self, x, y, nx, ny, max_steps=None):
        t = 0.
        for i in range(max_steps or self.MAX_STEPS):
            px, py = x + t * nx, y + t * ny
            d = self.distance_to(px, py)
            if d <= self.MIN_SURFACE:
                return t
            t += d * self.FUDGE
        return self.MAX_DISTANCE

    def save_png(self, file, width, height, bounding_box=None, quant=4):
        import png

        if bounding_box is None:
            bounding_box = self.bounding_box()
            bounding_box.adjust(-1,-1, 1,1)

        cache = dict()

        rows = []
        for py in range(height):
            y = bounding_box.min_y + bounding_box.height * (height-1-py) / height
            row = []
            for px in range(width):
                x = bounding_box.min_x + bounding_box.width * px / width
                if quant > 1:
                    index = ((px//quant)*quant, (py//quant)*quant)
                    if index not in cache:
                        cache[index] = self.distance_to(x, y)
                    d = cache[index]
                else:
                    d = self.distance_to(x, y)
                d = -min(0, d)*5
                rgb = [30, 30+d*100, 30+d*150]
                row += [max(0,min(255, int(c))) for c in rgb]
            rows.append(row)

        image = png.from_array(rows, "RGB")
        image.save(file)

    def to_json(self):
        return {
            "bbox": self.bounding_box().to_json(),
            "objects": [o.to_json() for o in self.objects],
        }

    @classmethod
    def from_json(cls, data):
        df = cls()
        for o in data["objects"]:
            if o["type"] == "point":
                df.add(Point(o["x"], o["y"]))
            elif o["type"] == "circle":
                df.add(Circle(o["x"], o["y"], o["radius"], o["inverted"]))
            elif o["type"] == "rectangle":
                df.add(Rectangle(o["x1"], o["y1"], o["x2"], o["y2"], o["inverted"]))
            elif o["type"] == "centered_rectangle":
                df.add(CenteredRectangle(o["x"], o["y"], o["width"], o["height"], o["inverted"]))
            else:
                raise ValueError("Invalid csg type '%s'" % o["type"])
        return df
