#!/usr/bin/env python
# $Id: perfCG.py,v 1.6 2003/07/16 13:50:11 pletzer Exp $
"""
Performance test
"""


import time, sys, string
import spla, reg2tri
from DirichletBound import DirichletBound
from math import sin, cos, pi

from ellipt2d import ellipt2d

xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
fact = 1
nx1 = ny1 = 20
if len(sys.argv)>1: nx1 = ny1 = int(sys.argv[1])
grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1, ny1)
print 'N=',len(grid)

db = DirichletBound()
for i in range(0,nx1):
    db[i] = 0.0
for i in range((ny1-1)*nx1, ny1*nx1):
    x = grid.x(i)
    db[i] = sin(pi*x)

F, g, s = '1.', '0.', '0.'
tic = time.time()
equ = ellipt2d(grid, F, g, s)
[amat, s] = equ.stiffnessMat()
equ.dirichletB(db,amat,s)
toc = time.time()
print 'time to assemble siffness matrix %10.2f secs'%(toc-tic)
v0 = s
v = amat.CGsolve(v0,s,1.0e-6, len(s) )
#v = spla.CGsolve(amat,v0,s,1.0e-6, len(s) )
tic = time.time()
print 'time CGPython %10.2f secs'% (tic-toc)
##import superlu
##v = superlu.solve(amat, s) 
##toc = time.time()
##print 'time to solve %10.2f secs'%(toc-tic)

print 'max(v)=',max(v),' min(v)=',min(v)

##from tkplot import *
##root = Tk() 
##frame = Frame(root) 
##frame.pack() 
##WIDTH, HEIGHT = 300, 300 
##button = Button(frame, text="OK", fg="red", command=frame.quit) 
##button.pack(side=BOTTOM) 
##canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
##canvas.pack() 
##tkplot(canvas, grid, v, 0, 0, 1, WIDTH, HEIGHT) 
##tkplot(canvas, grid, db, 1, 0, 1, WIDTH, HEIGHT) 
##root.mainloop()
