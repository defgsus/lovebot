import math

EPSILON = 0.00000001


def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


def solve_distance_constraint(x1, y1, x2, y2, rest_distance):
    dx = (x2 - x1)
    dy = (y2 - y1)
    d = math.sqrt(dx*dx+dy*dy)
    diff = d - rest_distance
    if abs(diff) < EPSILON:
        return 0., 0.
    return dx * diff, dy * diff


def collide_sphere_with_distancefield(x, y, radius, x_vel, y_vel, df):
    d = df.distance_to(x, y) - radius
    if d <= 0.:
        nx, ny = df.normal(x, y)
        return -d * nx, -d * ny
