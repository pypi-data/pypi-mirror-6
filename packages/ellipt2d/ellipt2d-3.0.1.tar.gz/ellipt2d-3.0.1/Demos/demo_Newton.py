#!/usr/bin/env python
#
# J. Mollis 8/1/2000


"""
This demo illustrates the Newton method for solving 
non-linear elliptic PDE's using ellipt2d.
"""

from math import sqrt, exp
from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
import reg2tri, vector
import time, os
from math import sqrt

N = 100
x0, y0 = 0.0, 0.0       
xmax, ymax = 1.0, 1.0 

nx1 = int(sqrt(N))
ny1 = int(sqrt(N))
nx1 = max(3, nx1)
ny1 = max(3, ny1)

grid = reg2tri.rect2cross((x0, y0, xmax, ymax), nx1, ny1)

db = DirichletBound()

for i in range(0,nx1):
    db[i] = 0.0
	
for i in range( (ny1-1)*(nx1) , (ny1-1)*(nx1)+ nx1 ):
    db[i] = 0.0

for i in range(0,ny1-1):
    db[(i)*nx1] = 0.0
    db[(i)*nx1 + nx1-1] = 0.0


#--------------

f = '1' # Always equal to one for the duration.


#Initial state ------

g, s = [], []

for i in range(0,len(grid)):
    g.append(-1.0)
    s.append(-1.0)

v = vector.zeros(len(grid))

ad = 1.0
while ad > 1.0e-6: 

    equ = ellipt2d(grid, f,g,s)
    [amat, s] = equ.stiffnessMat()
    equ.dirichletB(db,amat,s)
    
    vn = amat.CGsolve(v, s,(1.0e-3)/(float(N)))
	
    ad = 0.0
    for j in range(0,len(v)):
	ad = ad + abs(v[j]-vn[j])
	g[j] = -exp(-vn[j])
	s[j] = -exp(-vn[j]) - vn[j]*exp(-vn[j])
    ad = ad/len(v)
    v = vn


    #--------------

# plot result

from Tkinter import Tk, Frame, Button, Canvas, BOTTOM
import tkplot
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 500, 450 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack()
tkplot.tkplot(canvas, grid, v, 0,0,1, WIDTH, HEIGHT) 
tkplot.tkplot(canvas, grid, db, 0,0,1, WIDTH, HEIGHT) 
root.mainloop() 




















