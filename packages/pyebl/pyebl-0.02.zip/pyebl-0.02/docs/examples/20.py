#!/usr/bin/env python
import os
WD = os.path.abspath(os.curdir) + '\\'

##########
import pyebl as edw

def cross(cx=0.0, cy=0.0, size=10.0):
    h = float(abs(size))
    across = edw.poly(points=[(cx - h / 5, cy + h / 2), (cx + h / 5, cy + h / 2), (cx, cy), (cx + h / 2, cy + h / 5), (cx + h / 2, cy - h / 5),
                  (cx, cy), (cx + h / 5, cy - h / 2), (cx - h / 5, cy - h / 2), (cx, cy), (cx - h / 2, cy - h / 5), (cx - h / 2, cy + h / 5), (cx, cy)])
    return across


two_crosses = edw.layer(name="two_crosses") 

two_crosses.add(cross(cx=0,cy=0,size=50))
two_crosses.add(cross(cx=0,cy=0,size=50).rotate(45).move(200, 100))

edw.save(two_crosses, WD + "output/20.ely", format="ely, svg")
