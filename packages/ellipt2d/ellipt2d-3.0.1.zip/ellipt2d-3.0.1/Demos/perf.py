#!/usr/bin/env python
# $Id: perf.py,v 1.5 2003/07/16 13:50:11 pletzer Exp $

"""
Performance test
"""

import time, sys

from ellipt2d import ellipt2d
import reg2tri
from DirichletBound import DirichletBound
from math import sin, cos, pi

xmin, xmax, ymin, ymax = 0.0, 1.0, 0.0, 1.0
fact = 1
nx1 = ny1 = 20
if len(sys.argv)>1 : nx1 = ny1 = int(sys.argv[1])
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
import superlu
v = superlu.solve(amat, s) 
tic = time.time()
print 'time to solve %10.2f secs'%(tic-toc)
