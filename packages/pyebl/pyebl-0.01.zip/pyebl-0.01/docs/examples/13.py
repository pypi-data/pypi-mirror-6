import pyebl as edw

four_crects = edw.layer(name="four_rects")

four_crects.add(edw.crect(cx=0,cy=50,width=5,height=10))
four_crects.add(edw.crect(cx=-100,cy=150,width=15,height=20))
four_crects.add(edw.crect(cx=200,cy=-250,width=25,height=30))
four_crects.add(edw.crect(cx=-300,cy=-350,width=35,height=40))

edw.save(four_crects, WD + "output/13.ely", format="ely, svg")
