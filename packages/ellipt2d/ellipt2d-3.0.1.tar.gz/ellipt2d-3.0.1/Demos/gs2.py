#!/usr/bin/env python 
# $Id: gs2.py,v 1.5 2013/12/20 17:17:07 pletzer Exp $
# A. Pletzer Sept 19 2000 
 
""" 
Demo illustrating the Newton method for solving  
non-linear elliptic PDEs using ellipt2d. 
""" 

from ellipt2d import ellipt2d
from DirichletBound import DirichletBound
from sparse import dot
import reg2tri, vector, superlu
import time, os
from math import sqrt, pi, cos, sin, exp
 
 
N = 200 # total number of nodes (=nx1*ny1)

######## geometry ################################

xmin, ymin = 0.5, -1.
xmax, ymax = 1.5, +1.
dx, dy = xmax-xmin, ymax-ymin
nx1 = int(sqrt(N)*sqrt(dx/dy))
ny1 = int(sqrt(N)*sqrt(dy/dx))

nx1 = 12 # radial points
ny1 = 11 # poloidal points

N = nx1* ny1

triang = 0.8
elong = 1.7
x0, y0 = 1.0, 0.0
a = 0.8
b = 2.0*a
smin=0.01

xy = []
for j in range(nx1):
    xy.append([])
    for i in range(ny1):
        t = pi*float(i)/float(ny1-1)
        s = smin + (1.-smin)* float(j)/float(nx1-1)
        x = x0 + a*s**2 *cos(t + triang*s**2 *sin(t))
        y = y0 + b*s**2 *sin(t)
##        x = xmin + (xmax-xmin)*float(j)/float(nx1-1)
##        y = ymin + (ymax-ymin)*float(i)/float(ny1-1)
        xy[j].append((x, y))
        

grid = reg2tri.cross(xy)
##################################################
 
 
db = DirichletBound({}) 
 
	 
for i in range(ny1): 
    db[(i)*nx1 + nx1-1] = 0.0 
 
 
#db.plot(grid,1) 
 
#-------------- 
 
f = '1/x' # does not change 
 
# nonlinearity 
# F = -(pp*x + 1.0/x)*exp(-alpha/(v+delta)**beta) 
# dF/dv = -(pp*x + 1.0/x)*exp(-alpha/v) *beta*alpha/(v+delta)**(beta+1) 
 
pp0=20.0
alpha=0.10 
beta=1 
delta=0.1 
nbumpy=1 # number of bumps in y direction 
 
# initial state
v = vector.zeros(len(grid))
lx, ly = xmax - xmin, ymax - ymin
k_square = pi**2 *( 1./lx**2 + float(nbumpy)**2/ly**2)
vmag = (pp0*xmin*xmax)/k_square
  
g, s = [], [] 
pp=pp0
for i in range(len(v)): 
    x=grid.x(i) 
    y=grid.y(i) 
    dx, dy = x - xmin, y - ymin 
    v[i] = vmag*sin(dx*pi/lx)*sin(dy*pi/ly)**nbumpy 
    fnl = -(pp*x + 1.0/x)*exp(-alpha/(v[i]+delta)**beta) 
    dfnl= -(pp*x + 1.0/x)*exp(-alpha/(v[i]+delta)**beta) *beta*alpha/(v[i]+delta)**(beta+1) 
    g.append(dfnl) 
    s.append(dfnl*v[i] - fnl) 
 
# iterate... 
 
t0 = time.time() 
 
ad = 0.01
iter = 0 
tol =  1.e-3/float(N) # prescribed tolerance 
thistol = 1.0/float(N)# initial tolerance 
const=1.
pp=pp0
dp = pp0/2.
maxiter = 100
while ad > 1.0e-4 and iter < maxiter: 
 
    pp=pp + const*dp
 
    iter = iter + 1 
 
    equ = ellipt2d(grid, f,g,s) 
    [amat, rhs] = equ.stiffnessMat() 
    equ.dirichletB(db,amat,rhs) 
     
    thistol = max(thistol/float(iter**2), tol) 
    #vn = amat.CGsolve(v, rhs, thistol,len(v)) 
    vn = superlu.solve(amat, rhs) 
	 
    ad = 0.0 
    vmax, vmin = max(vn), min(vn)
    for i in range(len(v)): 
	#vn[i] = fabs(vn[i])
	ad = ad + abs(v[i]-vn[i]) 
        fnl = -(pp*x + 1.0/x)*exp(-alpha/(vn[i]+delta)**beta) 
        dfnl= -(pp*x + 1.0/x)*exp(-alpha/(vn[i]+delta)**beta) *beta*alpha/(vn[i]+delta)**(beta+1) 
	g[i] = dfnl 
	s[i] = dfnl*v[i] - fnl 
    ad = ad/(len(v)*(vmax-vmin)) 
    if  ad < 1.0e-6 and thistol > tol:  
	# refine refine tolerance 
	print 'Newton converged, but not to prescribed tolerance' 
	thistol = tol 
	#vn = amat.CGsolve(vn, rhs, tol,len(v)) 
	vn = superlu.solve(amat, rhs)
	ad = 0.0 
	for i in range(len(v)): 
	    #vn[i] = fabs(vn[i])
	    ad = ad + abs(v[i]-vn[i]) 
    v = vn 
 
    # energy
    energy = vector.dot(v, dot(amat, v))
    print 'iteration ',iter,' pp=',pp
    print 'norm diff ->%10.5f' % ad 
    print 'v_max=%10.5f' % vmax
    print 'v_min=%10.5f' % vmin
    print 'energy=%12.3e ' % energy 
    print '-'*20 

    if ad > 0.1: const = const/2.
    if ad > 1.0:
        # reverse
        pp = pp - const*dp
        const = const/2.
    if vmin < -0.1:        
        # and try with smaller step
        const = 0.
        maxiter = iter + 10
    #-------------- 

print 'Rough analytic estimate for v_max = %10.5f' % vmag
print 'total wall clock time %10.2f in secs' % (time.time()-t0) 


 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
