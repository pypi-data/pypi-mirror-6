#!/usr/bin/env python

"""
Example of domain triangulation
"""
import Ireg2tri, vector
from tkplot import *


####### geometry ########################### 
points =[(0.,0.),(0.,1.),(2., 3.), (5., 3.), (7., 1.), (7., 0.),
         (4.,0.), (4., 2.), (3., 2.), (3., 0.)]
regionlist=[(1.5, 1.5), (5.5, 1.5), (3.5,1.5)]
holelist = [(3.5,1.5)]

# define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))
initialAreaBound = 0.1
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist,regionlist, holelist)
grid = meshgen.triangulate()
#grid = meshgen.refine(1)
N = len(grid)
print 'No of nodes = ',N


###### initialize graphics ################ 
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 400, 300 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack() 

f = vector.zeros(N)
f[19] = 1.
import ellipt2d
equ = ellipt2d.ellipt2d(grid, '1.','0.','0')
tkplot(canvas, grid, f, 1, 1, 1, WIDTH, HEIGHT) 
root.mainloop()
     
 
