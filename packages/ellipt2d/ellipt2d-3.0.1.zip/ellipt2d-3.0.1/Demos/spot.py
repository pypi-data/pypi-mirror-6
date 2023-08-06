#!/usr/bin/env python
# $Id: spot.py,v 1.3 2013/12/20 17:17:07 pletzer Exp $
 
"""
Spot pattern generator
"""

from ellipt2d import ellipt2d
import Ireg2tri, vector, superlu
import time, os
from Tkinter import Tk, Canvas
from tkplot import tkplot
from math import sqrt

####### geometry ########################### 
points =[(0.,0.),(0.,0.3), (1.,0.9),(2.,1.3),(3.,1.8),
         (3.5,5.0),(3.7, 5.0), (4.5,2.2),(6.8,1.8),
         (7.2,2.5),(7.5,5.0),(7.8, 5.0), (9.,1.3),(13.,0.),
         (9.,-1.3),(7.8, -5.0), (7.5,-5.0),(7.2,-2.5),(6.8,-1.8),
         (4.5,-2.2),(3.7,-5.0),(3.5,-5.0),(3.,-1.8),(2.,-1.3),
         (1.,-0.9),(0.,-0.3)];
Lx, Ly = 9., 5.
# define segments if domain has concavities and/or
# inhomogeneous boundary conditions
seglist = []
for i in range(len(points)-1):
    seglist.append((i,i+1))
seglist.append((len(points)-1,0))
initialAreaBound = 5.0
meshgen = Ireg2tri.Ireg2tri(initialAreaBound)
meshgen.setUpConvexHull(points,seglist)
grid = meshgen.triangulate()
#grid = meshgen.refine(1)
N = len(grid)
print 'No of nodes = ',N

####### input parameters ################### 
 
gamma = 15.0 #9.0
d=10.0
rho = 18.5
a = 92.0 
alpha = 1.5
b = 64.0
K = 0.1

# stationary values
#us=10.0
vs=9.28922
us = a + alpha*(vs-b)
print 'steady state us=',us, ' vs=',vs
# discretization
dt = 0.5*min(Lx,Ly)/(max(1., d)*N)
nsteps = 10
fact = 1.0 # 1.0 for Newton
gact = 0.5 # 1.0 for pseudo-Newton 
######## functions ########################

def h(u,v):
    try:
        n = len(u)
        return rho*u*v/(vector.ones(n)+u+K*u*u)
    except: print 'type error in fct h'

def dhu(u,v):
    try:
        n = len(u)
        denom = vector.ones(n)+u+K*u*u
        return rho*(v*denom - u*(vector.ones(n)+2.*K*u)*v)/(denom*denom)
    except: print 'type error in fct dhu'

def dhv(u,v):
    try:
        n = len(u)
        return rho*u/(vector.ones(n)+u+K*u*u)
    except: print 'type error in fct dhv'

def gu(u,v):
    try:
        n = len(u)
        return (vector.ones(n)/dt) + gamma*(vector.ones(n) + fact*dhu(u,v)) 
    except: print 'type error in fct gu'
    
def gv(u,v):
    try:
        n = len(u)
        return (vector.ones(n)/dt) + gamma*(alpha*vector.ones(n) + fact*dhv(u,v))
    except: print 'type error in fct gv'

def su(u,v):
    try:
        n = len(u)
        return (u/dt) + gamma*(a*vector.ones(n) - h(u,v) + fact*dhu(u,v)*u)
    except: print 'type error in fct su'

def sv(u,v):
    try:
        n = len(u)
        return (v/dt) + gamma*(alpha*b*vector.ones(n) - h(u,v) + fact*dhv(u,v)*v)
    except: print 'type error in fct su'


###### initialize graphics ################ 
root = Tk() 
WIDTH, HEIGHT = 400, 300 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack() 
 
 
ones = vector.ones(N)
zeros = vector.zeros(N)
xs, ys = vector.zeros(N), vector.zeros(N)
for i in range(N):
    xs[i], ys[i] = grid.x(i), grid.y(i)

rand = vector.random(N,-1.0,1.0)
##u = us*(ones + 0.01*rand)
v = vs*(ones + 0.01*rand)
u = us*ones
modulation = vector.vector(vector.cos(35.45*xs*ys/Lx))*vector.vector(vector.cos(12.*ys*xs/Ly)) 
#v = vs*(ones + 0.01*modulation)
delu = zeros
delv = zeros



iszerou = (a*ones - u - h(u,v))
print 'min/max f function %10.6f %10.6f ' % (min(iszerou), max(iszerou))
 
iter = 0 
tol = 1.e-5
while iter < nsteps: 
 
    iter = iter + 1 

    print 'matrix assembly for u'
    equ = ellipt2d(grid, '1.', gu(u,v+gact*delv), su(u,v+gact*delv)) 
    [amatu, bvecu] = equ.stiffnessMat() 
    unew = superlu.solve(amatu, bvecu)

    delu = unew - u

    print 'matrix assembly for v'
    eqv = ellipt2d(grid, '%10.5f' % d , gv(u+gact*delu, v), sv(u+gact*delu,v)) 
    [amatv, bvecv] = eqv.stiffnessMat() 
    vnew = superlu.solve(amatv, bvecv)

    delv = vnew - v

    uv_diff = max(sqrt(vector.norm(delu)),sqrt(vector.norm(delv)))/N
    print uv_diff
    if iter > 1 and  uv_diff<tol: break

    # update
    u = unew
    v = vnew

    du = u - us*ones
    dv = v - vs*ones

    print '-'*20 
    print 'iteration ', iter
    print 'max(du)=%10.5f min(du)=%10.5f' % (max(du), min(du)) 
    print 'max(dv)=%10.5f min(dv)=%10.5f' % (max(dv), min(dv))

##########done!
tkplot(canvas, grid, du, 0, 0, 1, WIDTH, HEIGHT) 
root.mainloop()
     
 
