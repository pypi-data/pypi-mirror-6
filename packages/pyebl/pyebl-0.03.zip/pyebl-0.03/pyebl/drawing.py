from .shapes import poly


def cross(cx=0.0, cy=0.0, size=10.0):
    h = float(abs(size))
    across = poly(points=[(cx - h / 5, cy + h / 2), (cx + h / 5, cy + h / 2), (cx, cy), (cx + h / 2, cy + h / 5), (cx + h / 2, cy - h / 5),
                  (cx, cy), (cx + h / 5, cy - h / 2), (cx - h / 5, cy - h / 2), (cx, cy), (cx - h / 2, cy - h / 5), (cx - h / 2, cy + h / 5), (cx, cy)])
    return across


def cross_layer(layer, cx=0.0, cy=0.0, size=10.0):
    """
    Add cross of given size to a layer at point (cx, cy).
    """
    h = float(abs(size))
    poly(points=[(cx - h / 5, cy + h / 2), (cx + h / 5, cy + h / 2), (cx, cy),
         (cx + h / 5, cy - h / 2), (cx - h / 5, cy - h / 2), (cx, cy)], area_fast=0)

    poly(points=[(cx + h / 2, cy + h / 5), (cx + h / 2, cy - h / 5), (cx, cy),
         (cx - h / 2, cy - h / 5), (cx - h / 2, cy + h / 5), (cx, cy)], area_fast=90)

    layer.add(poly(points=[(cx - h / 5, cy + h / 2), (cx + h / 5, cy - h / 2),
              (cx - h / 5, cy - h / 2), (cx + h / 5, cy + h / 2)], area_fast=0))

    layer.add(poly(points=[(cx - h / 2, cy + h / 10), (cx + h / 2, cy - h / 10),
              (cx + h / 2, cy + h / 10), (cx - h / 2, cy - h / 10)], area_fast=90))


def mm_rect_closed(width=30.0, bar=2.0, gap=1.5, chamfer=0.25):
    """
    Demonstration of polygon primitive. h/t C. Lange.
    """
    w = width
    b = bar
    g = gap
    c = chamfer
    cap = 10

    rc = poly(points=[(0, 0)])

    # upper
    rc.add((-w / 2, 0))
    rc.add((-w / 2, w / 2 - c))
    rc.add((-w / 2 + c, w / 2))
    rc.add((+w / 2 - c, w / 2))
    rc.add((+w / 2, w / 2 - c))
    rc.add((+w / 2, 0))
    rc.add((+g / 2, 0))
    rc.add((+g / 2, cap / 2))
    rc.add((+g / 2 + b - c, cap / 2))
    rc.add((+g / 2 + b, cap / 2 - c))
    rc.add((+g / 2 + b, b / 2))
    rc.add((+w / 2 - b, b / 2))
    rc.add((+w / 2 - b, w / 2 - b - c))
    rc.add((+w / 2 - b - c, w / 2 - b))
    rc.add((-w / 2 + b + c, w / 2 - b))
    rc.add((-w / 2 + b, w / 2 - b - c))
    rc.add((-w / 2 + b, b / 2))
    rc.add((-g / 2 - b, b / 2))
    rc.add((-g / 2 - b, cap / 2 - c))
    rc.add((-g / 2 - b + c, cap / 2))
    rc.add((-g / 2, cap / 2))
    rc.add((-g / 2, 0))

    # lower
    rc.add((-w / 2, 0))
    rc.add((-w / 2, -w / 2 + c))
    rc.add((-w / 2 + c, -w / 2))
    rc.add((+w / 2 - c, -w / 2))
    rc.add((+w / 2, -w / 2 + c))
    rc.add((+w / 2, 0))
    rc.add((+g / 2, 0))
    rc.add((+g / 2, -cap / 2))
    rc.add((+g / 2 + b - c, -cap / 2))
    rc.add((+g / 2 + b, -cap / 2 + c))
    rc.add((+g / 2 + b, -b / 2))
    rc.add((+w / 2 - b, -b / 2))
    rc.add((+w / 2 - b, -w / 2 + b + c))
    rc.add((+w / 2 - b - c, -w / 2 + b))
    rc.add((-w / 2 + b + c, -w / 2 + b))
    rc.add((-w / 2 + b, -w / 2 + b + c))
    rc.add((-w / 2 + b, -b / 2))
    rc.add((-g / 2 - b, -b / 2))
    rc.add((-g / 2 - b, -cap / 2 + c))
    rc.add((-g / 2 - b + c, -cap / 2))
    rc.add((-g / 2, -cap / 2))
    rc.add((-g / 2, 0))

    return rc
