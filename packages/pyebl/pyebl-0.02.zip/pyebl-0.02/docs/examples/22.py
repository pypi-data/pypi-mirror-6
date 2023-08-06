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


align_and_square = edw.struct(name="align_and_square")
four_crosses = edw.layer(name="four_crosses")
square=edw.layer(name="square", fill_color="#FF0000")
align_and_square.add(four_crosses, square)

four_crosses.add(cross(cx=0,cy=0,size=10))
four_crosses.add(cross(cx=100,cy=0,size=10))
four_crosses.add(cross(cx=0,cy=100,size=10))
four_crosses.add(cross(cx=100,cy=100,size=10))

square.add(edw.crect(cx=50,cy=50,width=10,height=20))

edw.save(align_and_square, WD + "output/22", format="ely, svg")
