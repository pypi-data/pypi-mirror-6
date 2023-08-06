class Rect:

    """
    An eDraw rectangle shape.
    """
    tag = "RECT"

    def __init__(self, dose_factor=1.0, height=1.0, width=1.0, x=0.0, y=0.0, area_slow="left", area_fast=0.0):
        self.dose_factor = dose_factor
        self.height = height
        self.width = width
        self.x = x
        self.y = y
        self.area_slow = area_slow
        self.area_fast = area_fast

    def bounding_box(self):
        min_x = self.x
        max_x = self.x + self.width
        min_y = self.y
        max_y = self.y + self.height
        return (min_x, max_x, min_y, max_y)

    def get_attrib(self):
        return {"dose_factor": str(self.dose_factor), "height": str(self.height), "width": str(self.width), "x": str(self.x), "y": str(self.y), "area_slow": str(self.area_slow), "area_fast": str(self.area_fast) + " deg"}


class Polygon:

    """
    An eDraw polygon shape.
    """
    tag = "POLYGON"

    def __init__(self, points=None, dose_factor=1.0, area_fast=0.0, area_slow="left"):
        self.dose_factor = dose_factor
        self.area_fast = area_fast
        self.area_slow = area_slow
        if points == None:
            # Careful here!
            self.points = []
        else:
            # What if we pass one tuple as points?
            self.points = points

    def bounding_box(self):
        if (len(self.points) == 0):
            return (0, 0, 0, 0)
        for i, (x, y) in enumerate(self.points):
            if (i == 0):
                min_x, max_x = x, x
                min_y, max_y = y, y
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        return (min_x, max_x, min_y, max_y)

    def get_attrib(self):
        import re
        return {"dose_factor": str(self.dose_factor), "points": re.sub(r'[\[\]\,]', '', str(self.points)), "area_fast": str(self.area_fast) + " deg", "area_slow": str(self.area_slow)}

    def add(self, point):
        return self.points.append(point)

    def rotate(self, angle):
        import numpy as np
        c_a = np.cos(np.radians(angle))
        s_a = np.sin(np.radians(angle))
        self.points = [(p[0] * c_a - p[1] * s_a, p[0] * s_a + p[1] * c_a)
                       for p in self.points]
        return self

    def move(self, dx, dy):
        self.points = [(p[0] + dx, p[1] + dy) for p in self.points]
        return self

    def mirror_x(self, x=0):
        self.points = [(x + (x - p[0]), p[1]) for p in self.points]
        return self

    def mirror_y(self, y=0):
        self.points = [(p[0], y + (y - p[1])) for p in self.points]
        return self


class Lines:

    """
    An eDraw lines shape.
    """
    tag = "LINES"

    def __init__(self, points=None, dose_factor=1.0):
        self.dose_factor = dose_factor
        if points == None:
            # Careful here!
            self.points = []
        else:
            self.points = points

    def bounding_box(self):
        if (len(self.points) == 0):
            return (0, 0, 0, 0)
        for i, (x, y) in enumerate(self.points):
            if (i == 0):
                min_x, max_x = x, x
                min_y, max_y = y, y
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
        return (min_x, max_x, min_y, max_y)

    def get_attrib(self):
        import re
        return {"dose_factor": str(self.dose_factor), "points": re.sub(r'[\[\]\,]', '', str(self.points))}


def rect(**kwargs):
    return Rect(**kwargs)


def crect(cx=0.0, cy=0.0, width=1.0, height=1.0, **kwargs):
    """
    Rect centered at (cx,cy)
    """
    if "x" in kwargs or "y" in kwargs:
        raise TypeError(
            "Cannot provide both cx,cy coordinates and x,y coordinates!")

    return Rect(x=cx - width / 2.0, y=cy - height / 2.0, width=width, height=height, **kwargs)


def poly(**kwargs):
    return Polygon(**kwargs)


def poly_base_delta(base, delta, **kwargs):
    """
    Create polygon by providing a base point (base) as tuple and relative coordinates (delta) as list of tuples.
    """
    if "points" in kwargs:
        raise TypeError(
            "Cannot provide points to poly_base_delta function. Provide base as tuple and delta as list of tuples instead.")
    tmp_points = [base + d for d in delta]
    return Polygon(points=tmp_points, **kwargs)


def poly_incremental(base, incr, **kwargs):
    """
    Create polygon by providing a base point (base) as tuple and incremental relative coordinates (incr) as list of tuples.
    """
    tmp_points = [base]
    for i, p in enumerate(incr):
        tmp_points.append(
            (tmp_points[i][0] + incr[i][0], tmp_points[i][1] + incr[i][1]))
    return Polygon(points=tmp_points, **kwargs)


def line(**kwargs):
    return Lines(**kwargs)
