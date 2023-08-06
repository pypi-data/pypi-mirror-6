#!/usr/bin/env python
# $Id: simple2.py,v 1.4 2004/04/20 12:08:35 pletzer Exp $
import time

from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
from NeumannBound import NeumannBound
import reg2tri, superlu
from math import sin, cos, pi

"""
Simple demo
"""

xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
fact = 2
nx1, ny1 = fact*10, fact*10
grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1, ny1)

db = DirichletBound()
for i in range(nx1):
    db[i] = 0.
nb = NeumannBound()
for i in range((ny1-1)*nx1, ny1*nx1-1):
    x = grid.x(i)
    nb[(i+1,i)] = sin(pi*x)

F, g, s = '1.', '0.', '0.'
tic = time.time()
equ = ellipt2d(grid, F,g,s)
[amat, s] = equ.stiffnessMat()
equ.neumannB(nb, s)
equ.dirichletB(db,amat,s)
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
tkplot(canvas, grid, nb, 1, 0, 0, WIDTH, HEIGHT) 
tkplot(canvas, grid, db, 1, 0, 0, WIDTH, HEIGHT) 
root.mainloop()
