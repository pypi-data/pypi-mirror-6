import pyebl as edw

four_rects = edw.layer(name="four_rects")

four_rects.add(edw.rect(x=0,y=50,width=5,height=10))
four_rects.add(edw.rect(x=-100,y=150,width=15,height=20))
four_rects.add(edw.rect(x=200,y=-250,width=25,height=30))
four_rects.add(edw.rect(x=-300,y=-350,width=35,height=40))

edw.save(four_rects, WD + "output/12.ely", format="ely, svg")
