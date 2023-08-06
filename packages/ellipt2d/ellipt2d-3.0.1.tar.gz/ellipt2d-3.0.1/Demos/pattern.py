#!/usr/bin/env python
 
"""
Pattern generator
"""

from ellipt2d import *
from string import *
import Ireg2tri
import vector
import time
import os
from tkplot import *
import superlu

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
initialAreaBound = 0.05
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
grid = meshgen.triangulate()
#grid = meshgen.refine(1)


N = len(grid)
         

## xy = []
## x0 = 0.; x2 = 2.
## y0 = 0.; y1 = 0.2; y2=1.0
## dx = x2 - x0
## dy = 0.5*(y2+y1)-y0
 
## nx1 = int(sqrt(N)*sqrt(dx/dy))
## ny1 = int(sqrt(N)*sqrt(dy/dx))
## nx1 = max(3, nx1)
## ny1 = max(3, ny1)

## N = nx1*ny1

## for i in range(nx1):
##     dy = y1 - y0 + (y2-y1)*float(nx1-i-1)/float(nx1-1)
##     xy.append([])
##     for j in range(ny1):
##         x = x0 + dx * float(i)/float(nx1-1) 
##         y = y0 + dy * float(j)/float(ny1-1) 
##         xy[i].append((x,y)) 
 
 
## grid = reg2tri.criss(xy) 
#grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1,  ny1) 
 
####### input parameters ################### 
 
gamma = 25.0
d=7.0
rho = 5.0
a = 103.0 
alpha = 1.5 
b = 77.0
K = 0.125
 
 
###### initialize graphics ################ 
root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 500, 400 
#button = Button(frame, text="OK", fg="red", command=frame.quit) 
#button.pack(side=BOTTOM) 
#canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas2 = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
#canvas.pack() 
canvas2.pack() 
 
 
ones = vector.ones(N) 
zeros = vector.zeros(N)

u = a*ones
v = vector.random(N, 0, b/2.)  # b*ones + vector.random(N, 0, b/2.) 
 
u2 = u*u 
denom = ones + u + K*u2 
denom2 = denom*denom 
du = ones + 2.*K*u 
g = alpha*(b*ones-v) - rho*u*v/denom 
gu = - rho*v*(ones- u*du)/denom2 
gv = -alpha*ones - rho*u/denom 
f = a*ones - u - rho*u*v/denom 
fu = -ones - rho*v*(ones- u*du)/denom2 
fv = - rho*u/denom 
 
niter=100
iter = 0 
tol = 1.e-6 
ad=0.01
ad_opt = 100.0
while iter < niter and ad > tol: 
 
    iter = iter + 1 
     
    equ = ellipt2d(grid, '1.', -gamma*fu, gamma*(f-u*fu)) 
    [amatu, su] = equ.stiffnessMat() 
    u = superlu.solve(amatu, su) 
    for index in range(N): 
        u[index] = max(0., u[index]) 
    u2 = u*u 
    denom = ones + u + K*u2 
    denom2 = denom*denom 
    du = ones + 2.*K*u 
    g = alpha*(b*ones-v) - rho*u*v/denom 
    gu = - rho*v*(ones- u*du)/denom2 
    gv = -alpha*ones - rho*u/denom 
    f = a*ones - u - rho*u*v/denom 
    fu = -ones - rho*v*(ones- u*du)/denom2 
    fv = - rho*u/denom 
    eqv = ellipt2d(grid, '%10.5f' % d , -gamma*gv, gamma*(g-v*gv)) 
    [amatv, sv] = eqv.stiffnessMat() 
    #vnew = amatv.CGsolve(v, sv, tol, N) 
    vnew = superlu.solve(amatv, sv) 
    ad = 0. 
    for index in range(len(vnew)): 
        ad = ad + abs(vnew[index]-v[index])/float(N) 
        v[index] = max(0.,vnew[index]) 
     
    if ad < ad_opt:
        print '....saving solution in file pattern_{u,v}.inp' 
        equ.toUCD(u,  'pattern_u.inp'  )
        equ.toUCD(v,  'pattern_v.inp'  )
        ad_opt = ad
 
    print '-'*20 
    print 'iteration ', iter,' abs(vnew-v)=%10.6f' % ad 
    print 'max(u)=%10.5f min(u)=%10.5f' % (max(u), min(u)) 
    print 'max(v)=%10.5f min(v)=%10.5f' % (max(v), min(v)) 
#tkplot(canvas, grid, u, 1, 0, 1, WIDTH, HEIGHT) 
tkplot(canvas2, grid, v, 1, 0, 0, WIDTH, HEIGHT) 
root.mainloop()     
 
