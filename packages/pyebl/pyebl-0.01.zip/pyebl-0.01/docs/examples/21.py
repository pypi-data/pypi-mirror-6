import eDraw as edw

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

two_mms = edw.layer(name="two_mms") 

two_mms.add(mm_rect_closed(30, 2, 1.5, 0.25))
two_mms.add(mm_rect_closed(30, 2, 1.5, 0.25).rotate(45).move(200, 100))

edw.save(two_mms, WD + "output/21", format="ely, svg")
