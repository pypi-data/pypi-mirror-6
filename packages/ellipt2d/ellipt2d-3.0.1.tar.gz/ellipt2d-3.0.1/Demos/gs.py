#!/usr/bin/env python 
#
# $Id: gs.py,v 1.5 2013/12/20 17:17:07 pletzer Exp $
# A. Pletzer Sept 19 2000 
 
from ellipt2d import ellipt2d
import reg2tri, vector, superlu
from DirichletBound import DirichletBound
from sparse import dot
import time, os
from math import sqrt, pi, cos, sin, exp
from tkplot import *
 
 
 
""" 
This demo illustrates the Newton method for solving  
non-linear elliptic PDE's using ellipt2d. 
""" 
 
N = 400 # 1600 # total number of nodes (=nx1*ny1)

######## geometry ################################

xmin, ymin = 0.5, -1.
xmax, ymax = 1.5, +1.
dx, dy = xmax-xmin, ymax-ymin
nx1 = int(sqrt(N)*sqrt(dx/dy))
ny1 = int(sqrt(N)*sqrt(dy/dx))
N = nx1* ny1
grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1,  ny1)
##################################################
 
## root = Tk() 
## frame = Frame(root) 
## frame.pack() 
## WIDTH, HEIGHT = 400, 400 
## button = Button(frame, text="OK", fg="red", command=frame.quit) 
## button.pack(side=BOTTOM) 
## canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
## canvas.pack() 
 
## root.mainloop() 

db = DirichletBound() 
 
# South and North BCs 
for i in range(nx1): 
    db[i] = 0.0 
    db[i+(ny1-1)*nx1] = 0.0 
	 
# West and East BCs 
for i in range(ny1-1): 
    db[(i)*nx1] = 0.0 
    db[(i)*nx1 + nx1-1] = 0.0 
 
 
#db.plot(grid,1) 
 
#-------------- 
 
f = '1/x' # does not change 
 
# nonlinearity 
# F = -(pp*x + ggp/x)*exp(-alpha/(v+delta)**beta) 
# dF/dv = -(pp*x + ggp/x)*exp(-alpha/v) *beta*alpha/(v+delta)**(beta+1) 
 
pp0=100.0
ggp=100.0 
alpha=0.10 
beta=1 
delta=0.1 
nbumpy=1 # number of bumps in y direction 
 
# initial state
v = vector.zeros(len(grid))
lx, ly = xmax - xmin, ymax - ymin
k_square = pi**2 *( 1./lx**2 + float(nbumpy)**2/ly**2)
vmag = (pp0*xmin*xmax+ggp)/k_square
  
g, s = [], [] 
pp=pp0
for i in range(len(v)): 
    x=grid.x(i) 
    y=grid.y(i) 
    dx, dy = x - xmin, y - ymin 
    v[i] = vmag*sin(dx*pi/lx)*sin(dy*pi/ly)**nbumpy 
    fnl = -(pp*x + ggp/x)*exp(-alpha/(v[i]+delta)**beta) 
    dfnl= -(pp*x + ggp/x)*exp(-alpha/(v[i]+delta)**beta) *beta*alpha/(v[i]+delta)**(beta+1) 
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
dp = pp0/5.
maxiter = 4
while ad > 1.0e-4 and iter < maxiter:

    print 'iteration ', iter
 
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
        fnl = -(pp*x + ggp/x)*exp(-alpha/(vn[i]+delta)**beta) 
        dfnl= -(pp*x + ggp/x)*exp(-alpha/(vn[i]+delta)**beta) *beta*alpha/(vn[i]+delta)**(beta+1) 
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


 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
