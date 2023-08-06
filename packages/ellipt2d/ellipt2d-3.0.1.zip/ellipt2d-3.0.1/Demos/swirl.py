#!/usr/bin/env python 
# $Id: swirl.py,v 1.4 2013/12/20 17:17:07 pletzer Exp $
# A. Pletzer Dec 11 2000 
 
import sys 

from math import sqrt, exp, pi
import time, os
import reg2tri

from DirichletBound import DirichletBound
from ellipt2d import ellipt2d
import superlu, vector
from sparse import dot

from tkplot import * 

""" 
This demo illustrates the Newton method for solving  
non-linear elliptic PDE's using ellipt2d.

Grad Shafranov equation for the fire swirl problem
phys fluids vol 12 2859 (2000)
eq 23

"""

##################################################
N = 400 # total number of nodes (=nx1*ny1)

######## geometry ################################

xmin, ymin = 0.001, 0.0
xmax, ymax = +4.0, 20.
dx, dy = xmax-xmin, ymax-ymin
nx1 = int(sqrt(N)) # *sqrt(dx/dy))
ny1 = int(sqrt(N)) # *sqrt(dy/dx))
N = nx1* ny1
xy = []
for i in range(nx1):
	xi = xmin + (xmax-xmin)*(float(i)/float(nx1-1))**2
	xy.append([])
	for j in range(ny1):
		yj = ymin + (ymax-ymin)*(float(j)/float(ny1-1))**2
		xy[i].append((xi, yj))

#grid = reg2tri.rect2cross((xmin, ymin, xmax, ymax), nx1,  ny1)
grid = reg2tri.cross(xy)

#########input parameters##############################
sigma = 1.0
swirl= 0.6

########some functions#################################

def hp(v):
	return -2*(1.-v)

def hpp(v):
	return 2

def thetap(v):
	return -2*(1.-v)

def thetapp(v):
	return 2

def gamma2p(v):
	try:
		d = exp(v/(v-1.))
		return 2.*d*(1.-d)/(1.-v)**2
	except:
		# limit of v->1-
		return 0.
def gamma2pp(v):
	try:
		d = exp(v/(v-1.))
		return 2.*d*(1.+2.*v*(d-1.))/(1.-v)**4
	except:
		# limit of v->1-
		return 0.

def srhs(x, y, v):
	return -(x**2/(2.*pi**2)) * (sigma**2 * hp(v) + y*thetap(v)) + 2.*swirl**2 *gamma2p(v)

def dsrhs(x, y, v):
	return -(x**2/(2.*pi**2)) * (sigma**2 * hpp(v) + y*thetapp(v)) + 2.*swirl**2 *gamma2pp(v)
	
		

 
 
db = DirichletBound() 

# South BCs 
for i in range(nx1-1):
    x, y = grid.x(i), grid.y(i)
    db[i] = 1.0 - exp(-x**2-y**2)

	 
# West BCs 
for i in range(ny1-1): 
   index = 1 + (i+1)*nx1
   db[index] = 0.0 

root = Tk() 
frame = Frame(root) 
frame.pack() 
WIDTH, HEIGHT = 100, 400 
button = Button(frame, text="OK", fg="red", command=frame.quit) 
button.pack(side=BOTTOM) 
canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
canvas.pack() 
tkplot(canvas, grid, db, 1, 0, 0, WIDTH, HEIGHT) 
root.mainloop() 
#-------------- 
 
f = '1/x' # does not change 
 
# initial state
v = vector.zeros(len(grid))
  
g, s = [], [] 
for i in range(len(v)):
	x = grid.x(i)
	y = grid.y(i)
	vi = 1. - exp(-x**2)
	v[i] = vi
	ds = dsrhs(x, y, vi)
	g.append(-ds)
	s.append(srhs(x, y, vi) - vi*ds)


# iterate... 
 
t0 = time.time() 
 
ad = 0.01
iter = 0 
tol =  1.e-3/float(N) # prescribed tolerance 
thistol = 1.e-2/float(N)# initial tolerance 
const=1.
maxiter = 100
while ad > 1.0e-5 and iter < maxiter: 
 
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
	x = grid.x(i)
	y = grid.y(i)
	vi = min(vn[i], 1.0)
	vn[i] = vi
	vi = max(vn[i], 0.0)
	ad = ad + abs(v[i]-vi)
	ds = dsrhs(x, y, vi)
	g[i] = -ds
	s[i] = srhs(x, y, vi) - vi*ds
 
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
    print 'iteration ',iter,
    print 'norm diff ->%10.5f' % ad 
    print 'v_max=%10.5f' % vmax
    print 'v_min=%10.5f' % vmin
    print 'energy=%12.3e ' % energy 
    print '-'*20 
    equ.toUCD(v,  'swirl.inp'  ) 

    if ad > 0.1: const = const/2.
    if vmin < -0.1:        
        # and try with smaller step
        const = 0.
        maxiter = iter + 10
    #-------------- 
 
 
 
 
print 'total wall clock time %10.2f in secs' % (time.time()-t0) 


 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
