#!/usr/bin/env python
# $Id: simple3.py,v 1.3 2003/06/23 02:32:04 pletzer Exp $
import time
from math import pi, sin, cos
from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
from RobinBound import RobinBound
import reg2tri

xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
fact = 2
nx1, ny1 = fact*10, fact*10
grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1, ny1)

db = DirichletBound()
for i in range(nx1):
    db[i] = 0.
rb = RobinBound()
for i in range((ny1-1)*nx1, ny1*nx1-1):
    x = grid.x(i)
    rb[(i+1,i)] = (-1.0, sin(pi*x))

F, g, s = '1.', '0.', '0.'
tic = time.time()
equ = ellipt2d(grid, F,g,s)
[amat, s] = equ.stiffnessMat()
equ.robinB(rb, amat, s)
equ.dirichletB(db,amat,s)
##toc = time.time()
##print 'time to assemble siffness matrix %10.2f secs'%(toc-tic)
##v0 = s; v = amat.CGsolve(v0,s,1.0e-6, len(s) )
##tic = time.time()
##print 'time CGPython %10.2f secs'% (tic-toc)
import superlu
v = superlu.solve(amat, s) 
toc = time.time()
print 'time to solve %10.2f secs'%(toc-tic)

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
#tkplot(canvas, grid, v, 0, 0, 1, WIDTH, HEIGHT) 
tkplot(canvas, grid, rb, 1, 0, 0, WIDTH, HEIGHT) 
tkplot(canvas, grid, db, 1, 0, 0, WIDTH, HEIGHT) 
root.mainloop()
