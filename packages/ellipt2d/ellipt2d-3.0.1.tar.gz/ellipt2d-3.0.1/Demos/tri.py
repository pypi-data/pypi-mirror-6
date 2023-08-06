#!/usr/bin/env python
import sys
 
import Ireg2tri
from tkplot import *

points =[(0.,0.),(0.,0.3), (1.,0.9),(2.,1.3),(3.,1.8),
         (3.5,5.0),(3.7, 5.0), (4.5,2.2),(6.8,1.8),
         (7.2,2.5),(7.5,5.0),(7.8, 5.0), (9.,1.3),(13.,0.),
         (9.,-1.3),(7.8, -5.0), (7.5,-5.0),(7.2,-2.5),(6.8,-1.8),
         (4.5,-2.2),(3.7,-5.0),(3.5,-5.0),(3.,-1.8),(2.,-1.3),
         (1.,-0.9),(0.,-0.3)];
# define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))
initialAreaBound = 0.5
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
grid = meshgen.triangulate()
grid = meshgen.refine(1)

print '%d nodes' % len(grid)


root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 300, 250 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack()
tkplot(canvas, grid, [], 1, 0, 0, WIDTH, HEIGHT) 
root.mainloop() 
     
 
