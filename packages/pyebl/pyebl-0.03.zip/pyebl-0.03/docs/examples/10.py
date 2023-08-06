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

four_crosses = edw.layer(name="four_crosses")

four_crosses.add(cross(cx=0,cy=0,size=10))
four_crosses.add(cross(cx=60,cy=0,size=10))
four_crosses.add(cross(cx=0,cy=75,size=10))
four_crosses.add(cross(cx=60,cy=-25,size=10))

edw.save(four_crosses, WD + "output/10", format="ely, svg")
