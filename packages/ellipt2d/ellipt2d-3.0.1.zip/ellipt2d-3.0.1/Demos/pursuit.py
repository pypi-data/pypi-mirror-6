#!/usr/bin/env python
 
from ellipt2d import *
from string import *
import Ireg2tri 
import vector
import time
import os
from tkplot import *
import superlu

"""
Pattern generator test
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
initialAreaBound = 0.2
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
grid = meshgen.triangulate()
#grid = meshgen.refine(1)


N = len(grid)
         
 
####### input parameters ################### 

dt = 0.1
d  = 2.0
a  = 1.2
b= 1.4
 
 
###### initialize graphics ################ 
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 400, 200 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas2 = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack() 
canvas2.pack() 
 
 
ones = vector.ones(N) 
zeros = vector.zeros(N)

u = ones + vector.random(N, 0, 0.5) 
v = ones + vector.random(N, 0, 0.5) 
 
fu = d*ones
fv = ones
 
niter=4 
iter = 0 
tol = 1.e-6 
ad=0.01
ad_opt = 100.0
while iter < niter and ad > tol: 
 
    iter = iter + 1 
     
    gu = (1./dt - 1.)*ones + u + v
    su = u/dt
    equ = ellipt2d(grid, fu, gu, su) 
    [amatu, su] = equ.stiffnessMat() 
    u = superlu.solve(amatu, su) 
    for index in range(N): 
        u[index] = max(0., u[index])
        
    gv = (1./dt + a*b)*ones - a*u
    sv = v/dt    
    eqv = ellipt2d(grid, fv, gv, sv)
    
    [amatv, sv] = eqv.stiffnessMat() 
    vnew = superlu.solve(amatv, sv) 
    ad = 0. 
    for index in range(len(vnew)): 
        ad = ad + abs(vnew[index]-v[index])/float(N) 
        v[index] = max(0.,vnew[index]) 
     
    if ad < ad_opt:
        print '.....saving solution in file pursuit_u.inp' 
        equ.toUCD(u,  'pursuit_u.inp'  )
        print '.....saving solution in file pursuit_v.inp' 
        equ.toUCD(v,  'pursuit_v.inp'  )
        ad_opt = ad
 
    tkplot(canvas, grid, u, 1, 0, 1, WIDTH, HEIGHT) 
    tkplot(canvas2, grid, v, 1, 0, 1, WIDTH, HEIGHT) 
    print '-'*20 
    print 'iteration ', iter,' abs(vnew-v)=%10.6f' % ad 
    print 'max(u)=%10.5f min(u)=%10.5f' % (max(u), min(u)) 
    print 'max(v)=%10.5f min(v)=%10.5f' % (max(v), min(v)) 
     
 
