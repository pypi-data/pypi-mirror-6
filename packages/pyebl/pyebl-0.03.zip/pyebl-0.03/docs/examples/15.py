#!/usr/bin/env python
import os
WD = os.path.abspath(os.curdir) + '\\'

##########
import pyebl as edw

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

mm_rc_a = edw.layer(name="mm_rect_closed_array", fill_color="#7F2AFF")

width=30.0
w=width
bar=2.0
b=bar
gap=1.5
g=gap
chamfer=0.25
c=chamfer

nx=10
ny=9
mulx=4
muly=4
dx=25.0
dy=25.0
mdx=3
mdy=3
dangle=1

angle = 0
for iy in range(ny):
    for ix in range(nx):
        for imulx in range(mulx):
            for imuly in range(muly):
                mm_rc_a.add( mm_rect_closed(width=w,bar=b,gap=g,chamfer=c).rotate(angle).move((mulx * ix + imulx) * (dx+w) + ix * mdx, (muly * iy + imuly) * (dy+w) + iy * mdy) )
        angle = angle + dangle

edw.save(mm_rc_a, WD + "output/15", format="ely, svg")
