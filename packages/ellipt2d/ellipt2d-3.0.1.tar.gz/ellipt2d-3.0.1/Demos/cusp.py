#!/usr/bin/env python

"""
Cusp test
"""

import time
import reg2tri, vector
from DirichletBound import DirichletBound
from ellipt2d import ellipt2d
from sparse import dot
from math import pi

xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
fact = 1
nx1, ny1 = fact*20, fact*10
grid = reg2tri.rect2crisscross((xmin, ymin, xmax, ymax), nx1, ny1)
N=len(grid)

F = vector.ones(N)
for i in range(N):
    x, y = grid.x(i), grid.y(i)
    if x>0.5*xmax: F[i] = -1.0

db = DirichletBound()
for i in range(ny1):
    ileft, irigh = i*(2*nx1-1), i*(2*nx1-1) + nx1 - 1
    db[ileft] = 0.0 #sin(2.*pi*grid.y(ileft))
    db[irigh] = 1.0 #sin(2.*pi*grid.y(irigh))

    
for i in range(nx1):
    x = grid.x(i)
    db[i] = 0.0 # sin(pi*x)

for i in range((ny1-1)*(2*nx1-1), 2*ny1*nx1-nx1-ny1+1):
    x = grid.x(i)
    db[i] = 0.0 

g, s = '%10.6f' % (0.*pi**2/xmax**2), '0.'
tic = time.time()
equ = ellipt2d(grid, F,g,s)
[amat, s] = equ.stiffnessMat()
equ.dirichletB(db,amat,s)
toc = time.time()
print 'time to assemble siffness matrix %10.2f secs'%(toc-tic)
#v0 = s; v = amat.CGsolve(v0,s,1.0e-6, len(s) )
tic = time.time()
#print 'time CGPython %10.2f secs'% (tic-toc)
import superlu
v = superlu.solve(amat, s)
toc = time.time()
print 'time to solve %10.2f secs'%(toc-tic)

# check
print vector.sum(dot(amat, v) - s)

print 'max(v)=',max(v),' min(v)=',min(v)

from tkplot import *
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 300, 300 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack() 
tkplot(canvas, grid, v, 0, 0, 1, WIDTH, HEIGHT) 
tkplot(canvas, grid, db, 0, 0, 1, WIDTH, HEIGHT) 
root.mainloop()
