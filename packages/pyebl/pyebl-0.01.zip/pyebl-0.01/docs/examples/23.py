import pyebl as edw

def cross(cx=0.0, cy=0.0, size=10.0):
    h = float(abs(size))
    across = edw.poly(points=[(cx - h / 5, cy + h / 2), (cx + h / 5, cy + h / 2), (cx, cy), (cx + h / 2, cy + h / 5), (cx + h / 2, cy - h / 5),
                  (cx, cy), (cx + h / 5, cy - h / 2), (cx - h / 5, cy - h / 2), (cx, cy), (cx - h / 2, cy - h / 5), (cx - h / 2, cy + h / 5), (cx, cy)])
    return across


pitch=1
electrode_width=0.5
overlap=1.0/3
repetitions=100
height=100
spacing=100

p = pitch
a = electrode_width
h = height
o = overlap
N = repetitions
d = spacing

total_width = 2*N*p + d

sample_23 = edw.struct(name="23")
IDT = sample_23.add(name="IDT_layer", fill_color="#0000FF")

# draw left IDT, bottom
for i in range(N):
    IDT.add(edw.rect(dose_factor=0.5, height=h, width=a, y=-h/2.0, x=-total_width/2 + i*p))

# draw left IDT, top
for i in range(N):
    IDT.add(edw.rect(dose_factor=0.5, height=h, width=a*o, y=-h/2.0, x=((2*(-total_width/2 + i*p) + a)/2 - a*o/2) ))

# draw right IDT, bottom
for i in range(N):
    IDT.add(edw.rect(dose_factor=0.5, height=h, width=a, y=-h/2.0, x=d/2 + i*p))

# draw right IDT, top
for i in range(N):
    IDT.add(edw.rect(dose_factor=0.5, height=h, width=a*o, y=-h/2.0, x=((2*(d/2 + i*p) + a)/2 - a*o/2) ))

alignment = sample_23.add(name="alignment", fill_color="#FF0000")

alignment.add(cross(cx=-total_width/2, cy=height, size=height/5.0))
alignment.add(cross(cx=total_width/2, cy=height, size=height/5.0))
alignment.add(cross(cx=-total_width/2, cy=-height, size=height/5.0))
alignment.add(cross(cx=total_width/2, cy=-height, size=height/5.0))

FM = sample_23.add(name="FM", fill_color="#00FF00")

FM.add(edw.crect(cx=0,cy=0,width=20,height=20))

edw.save(sample_23, WD + "output/23", format="ely, svg")
