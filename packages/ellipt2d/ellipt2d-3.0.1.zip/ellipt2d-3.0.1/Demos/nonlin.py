#!/usr/bin/env python
# $Id: nonlin.py,v 1.3 2013/12/20 17:17:07 pletzer Exp $

from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
import Ireg2tri, superlu, vector
import time, os
from Tkinter import Tk, Canvas
from tkplot import tkplot

"""
pattern generator
"""

####### geometry ########################### 
points =[(0.,0.),(0.,0.3), (1.,0.9),(2.,1.3),(3.,1.8),
         (3.5,5.0),(3.7, 5.0), (4.5,2.2),(6.8,1.8),
         (7.2,2.5),(7.5,5.0),(7.8, 5.0), (9.,1.3),(13.,0.),
         (9.,-1.3),(7.8, -5.0), (7.5,-5.0),(7.2,-2.5),(6.8,-1.8),
         (4.5,-2.2),(3.7,-5.0),(3.5,-5.0),(3.,-1.8),(2.,-1.3),(1.,-0.9),(0.,-0.3)];
# need to define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))

dB = DirichletBound()
for i in range(len(points)):
    dB[i] = 0.0

initialAreaBound = 0.1
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)

meshgen.setUpDirichlet(dB)

grid = meshgen.triangulate()
#grid = meshgen.refine(1)


N = len(grid)
          
####### input parameters ################### 

K=500.0
u0=1.0
dt = 0.002
 
###### initialize graphics ################ 
root = Tk() 
WIDTH, HEIGHT = 300, 200 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack() 
 
 
ones = vector.ones(N) 
zeros = vector.zeros(N)

u = vector.random(N, -10.*u0, 10.*u0) 
u2 = u*u

f = dt*ones
g = ones - (dt*K*ones)/(u2 + u0**2 *ones)
s = u

 
niter=4
iter = 0 
tol = 1.e-5
ad=0.01
ad_opt = 100.0
tim=0.
while iter < niter and ad > tol:

    tim += dt
 
    iter = iter + 1 
     
    equ = ellipt2d(grid, f, g, s) 
    [amatu, su] = equ.stiffnessMat()
    #equ.dirichletB(dB,amatu,su)
    u = superlu.solve(amatu, su)
    
    ad = 0. 
    for index in range(len(u)): 
        ad = ad + abs(u[index]-s[index])/float(N)

    if ad < ad_opt:
        print '....save solution in file nonlin.inp' 
        equ.toUCD(u,  'nonlin.inp'  )
        ad_opt = ad

    u2 = u*u
    g = ones - (dt*K*ones)/(u2 + u0**2 *ones)
    s = u
     
 
    tkplot(canvas, grid, u, 1, 0, 1, WIDTH, HEIGHT) 
    print '-'*20 
    print iter,' time:%10.6f' % tim, ' abs(unew-u)=%10.6f' % ad
    maxu, minu = max(u), min(u)
    print 'max(u)=%10.5f min(u)=%10.5f diff(u)=%10.5f' % (maxu, minu, maxu-minu)

root.mainloop()
 
