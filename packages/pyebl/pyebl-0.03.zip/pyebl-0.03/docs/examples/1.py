#!/usr/bin/env python
import os
WD = os.path.abspath(os.curdir) + '\\'

##########
import pyebl as edw

edw.save(edw.rect(x=0,y=0,width=10,height=20), WD + "output/1.ely", format="ely")
edw.save(edw.rect(x=0,y=0,width=10,height=20), WD + "output/1.svg", format="svg")
