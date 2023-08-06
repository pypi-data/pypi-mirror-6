import pyebl as edw

side = 3**7 # some big multiple of 3
sierpinski = edw.layer(name="sierpinski", fill_color="#0000FF")

def scarpet(layer, x=0, y=0, length=3**7, min_size=9):
    step=length/3.0
    square = edw.rect(x=x+step, y=y+step, width=step, height=step)
    layer.add(square)
    if (length > min_size):
        # left 3
        scarpet(layer, x, y, length/3, min_size)
        scarpet(layer, x, y+step, length/3, min_size)
        scarpet(layer, x, y+step*2, length/3, min_size)
        # upper & lower
        scarpet(layer, x+step, y, length/3, min_size)
        scarpet(layer, x+step, y+step*2, length/3, min_size)
        # right 3
        scarpet(layer, x+step*2, y, length/3, min_size)
        scarpet(layer, x+step*2, y+step, length/3, min_size)
        scarpet(layer, x+step*2, y+step*2, length/3, min_size)

scarpet(sierpinski, x=0, y=0, length=3**7, min_size=9)

edw.save(sierpinski, WD + "output/7", format="ely, svg")
