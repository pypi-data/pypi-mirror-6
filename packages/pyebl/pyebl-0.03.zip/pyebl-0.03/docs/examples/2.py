#!/usr/bin/env python
import os
WD = os.path.abspath(os.curdir) + '\\'

##########
import pyebl as edw

edw.save(edw.rect(x=25,y=50,width=10,height=20), WD + "output/2", format="ely, svg")
