#!/usr/bin/env python
# $Id: jump.py,v 1.9 2013/12/20 17:17:07 pletzer Exp $

"""
Demo with discontinuous f function 
"""

from cellipt2d import *
import cmath, csuperlu, csparse, tkplot, vector, reg2tri
import time, sys, Tkinter
from math import pi


TWOPI = 2.*pi

########### input data ###########################################
L = TWOPI
Lx, Ly = L, L
xmin, xmax, ymin, ymax = 0., Lx, 0., Ly # box size
lambda0 = + (2.*pi/L)**2 *cmath.exp(1j*0.00)# lambda will be a factor of this

nx1 = 3 #23
if len(sys.argv)>1: nx1 = int(sys.argv[1]) # no of cells in each direction
ny1 = nx1
dm, dn = 0., 0.5 # boundary phase shift is dm*2*pi, resp. dn*2*pi
xcentre, ycentre, hole_size= L/2., L/2., 1.5*L/5. # plasma location and radius
beta = 4.0/nx1 # layer width (normalized)
alpha= 1.0 # one for square / zero for circle
Fhole = -1.0/0.3333

# controls
lsquare = 0.7 # initial guess
niter = 11 # max no of inverse iterations
tol = 1.e-6 # tolerance in eigensolver
should_i_correct_F = 1
should_i_plot = 1
should_i_probe = 0
should_i_checkBCs = 0
probe_x, probe_y, probe_h = xcentre+hole_size/2., ycentre, 0.05*L

##################################################################

# mesh
grid = reg2tri.rect2crisscross((xmin, ymin, xmax, ymax), nx1, ny1)
N=len(grid)
print '%d finite elements' % N

# PDE operator is -div F. grad v + g v = s

# set F
F = vector.ones(N)
scrit = 1.0 - 2.*beta
for i in range(N):
    x2 = (grid.x(i)-xcentre)**2/hole_size**2
    y2 = (grid.y(i)-ycentre)**2/hole_size**2
    s = x2 + y2 - alpha * x2 * y2
    if x2 > 1.0 or y2 > 1. : s = 3.0
    expfct = exp(-(s - scrit)/beta)
    try:
        F[i] = Fhole + (1.0 - Fhole)/(1.0 - expfct)
    except:
        F[i] = 1.0
    #F[i] = min(max(F[i], -10.), 10.)

tic = time.time()
# build amat
stiff = ellipt2d(grid, F, '0.', '0.')

if should_i_correct_F:
    # correct F
    for it in stiff.cells.data.keys():
        (x, y) = stiff.cells.centre(it)
        x2 = (x-xcentre)**2/hole_size**2
        y2 = (y-ycentre)**2/hole_size**2
        s =  x2 + y2 - alpha * x2 * y2
        if x2 > 1.0 or y2 > 1. : s = 3.0
        expfct = exp(-(s - scrit)/beta)
        try:
            funct = Fhole + (1.0 - Fhole)/(1.0 - expfct)
        except: funct = 1.0
        #funct = min(100., max(-100., funct))
        stiff.fCells[it] = funct
        stiff.fCells[it] = funct



[amat, rhs] = stiff.stiffnessMat()

# build bmat
lump = ellipt2d(grid, '0.', '1.', '0.0')
[bmat, rhs] = lump.stiffnessMat()
print ' -> time to assemble a and b %10.3f ' % (time.time()-tic)

# Apply phase shifted boundary conditions
#########################################
cx, cy = cmath.exp(1j*dm*TWOPI), cmath.exp(1j*dn*TWOPI)

# west/east
for i in range(1, ny1-1):
    iw, ie = i*(2*nx1-1), i*(2*nx1-1) + nx1 - 1
    amat[(iw,iw)] += amat[(ie,ie)]
    amat[(ie,ie)]  = amat[(iw,iw)]
    bmat[(iw,iw)] += bmat[(ie,ie)]
    bmat[(ie,ie)]  = bmat[(iw,iw)]
    neighbors = grid[ie][1]
    for j in neighbors:
        amat[(iw, j)] = amat[(ie, j)] / cx
        bmat[(iw, j)] = bmat[(ie, j)] / cx
    neighbors = grid[iw][1]
    for j in neighbors:
        amat[(ie, j)] = amat[(iw, j)] * cx
        bmat[(ie, j)] = bmat[(iw, j)] * cx

# south/north
for i in range(1, nx1-1):
    js, jn = i, i + (ny1-1)*(2*nx1-1)
    amat[(js,js)] += amat[(jn,jn)]
    amat[(jn,jn)]  = amat[(js,js)]
    bmat[(js,js)] += bmat[(jn,jn)]
    bmat[(jn,jn)]  = bmat[(js,js)]
    neighbors = grid[jn][1]
    for j in neighbors:
        amat[(js, j)] = amat[(jn, j)] / cy
        bmat[(js, j)] = bmat[(jn, j)] / cy
    neighbors = grid[js][1]
    for j in neighbors:
        amat[(jn, j)] = amat[(js, j)] * cy
        bmat[(jn, j)] = bmat[(js, j)] * cy

# corners sw, se, ne, nw
isw, ise, ine, inw = 0, nx1-1, N-1, (ny1-1)*(2*nx1-1)
amat[(isw,isw)] += amat[(ise,ise)] + amat[(ine,ine)] + amat[(inw,inw)]
amat[(ise,ise)] = amat[(isw,isw)]
amat[(ine,ine)] = amat[(isw,isw)]
amat[(inw,inw)] = amat[(isw,isw)]
neighbors = grid[isw][1]
for j in neighbors:
    amat[(ise,j)] = amat[(isw,j)] * cx
    amat[(ine,j)] = amat[(isw,j)] * cx * cy
    amat[(inw,j)] = amat[(isw,j)] * cy
neighbors = grid[ise][1]
for j in neighbors:
    amat[(isw,j)] = amat[(ise,j)] / cx
    amat[(ine,j)] = amat[(ise,j)] * cy
    amat[(inw,j)] = amat[(ise,j)] * cy / cx
neighbors = grid[ine][1]
for j in neighbors:
    amat[(isw,j)] = amat[(ine,j)] / cx / cy
    amat[(ise,j)] = amat[(ine,j)] / cy
    amat[(inw,j)] = amat[(ine,j)] / cx
neighbors = grid[inw][1]
for j in neighbors:
    amat[(isw,j)] = amat[(inw,j)] / cy
    amat[(ise,j)] = amat[(inw,j)] * cx / cy
    amat[(ine,j)] = amat[(inw,j)] * cx
    

lsq = lsquare

# initial eigenvector
v = cvector.random(N, 0.,1.+0j) # initial guess
for i in range(N):
    x, y = grid.x(i), grid.y(i)
    v[i] = cmath.exp(dm*x*1j + dn*y*1j)

for i in range(ny1):
    iw, ie = i*(2*nx1-1), i*(2*nx1-1) + nx1 - 1
    v[ie] = cx*v[iw]
for i in range(nx1):
    js, jn = i, i + (ny1-1)*(2*nx1-1)
    v[jn] = cy*v[js]



lambd = lsq * lambda0

# seek eigensolution

##print 'amat'
##amat.out()
##print 'bmat'
##bmat.out()

#bmat.plot()
print 'v=', v

tic = time.time()
[lambd, v, residue, iter] = csuperlu.eigen(amat, bmat, lambd, v, tol, niter)
print ' -> time to solve eigensystem: %8.2f s' % (time.time()-tic)

print 'lambd=', lambd
print 'v=', v
print 'residue=', residue
print 'niter=', niter


# want phase = 0 for v(0,0)
coeff = abs(v[0])/v[0]+0j
v = v*coeff

print 'N=', N

if should_i_probe:
    # probing solution
    import cell
    cells =cell.cell(grid)
    v0 = cells.interp(v, probe_x  ,probe_y  )
    vn = cells.interp(v, probe_x  ,probe_y+probe_h)
    vs = cells.interp(v, probe_x  ,probe_y-probe_h)
    vw = cells.interp(v, probe_x-probe_h,probe_y  )
    ve = cells.interp(v, probe_x+probe_h,probe_y  )
    del2_v = (vn+vs+vw+ve-4.*v0)/probe_h**2
    lam_v0 = lambd*v0

    print 'v0 = (%10.6f, %10.6f)'%(v0.real, v0.imag)
    print 'vn = (%10.6f, %10.6f)'%(vn.real, vn.imag)
    print 'vs = (%10.6f, %10.6f)'%(vs.real, vs.imag)
    print 've = (%10.6f, %10.6f)'%(ve.real, ve.imag)
    print 'vw = (%10.6f, %10.6f)'%(vw.real, vw.imag)

    print 'del2_v.real=', del2_v.real
    print 'del2_v.imag=', del2_v.imag
    print \
          """Probing solution at (%10.6f,%10.6f)
          -del2_v  = (%10.6f,%10.6f)
          lambda*v = (%10.6f,%10.6f)""" \
          % (probe_x,probe_y, -del2_v.real, \
             -del2_v.imag, lam_v0.real, lam_v0.imag)
    dve, dvw = (ve-v0)/probe_h, -(vw-v0)/probe_h
    dvn, dvs = (vn-v0)/probe_h, -(vs-v0)/probe_h
    print \
          """Slopes:\n
          E: (%10.6f,%10.6f) W: (%10.6f,%10.6f)\n
          N: (%10.6f,%10.6f) S: (%10.6f,%10.6f)""" \
          % (dve.real, dve.imag, dvw.real, dvw.imag, \
             dvn.real, dvn.imag, dvs.real, dvs.imag)


if should_i_checkBCs:
    for i in range(nx1):
        ibot, itop = i, i + (ny1-1)*(2*nx1-1)
        print 'S/N %d: abs=%10.6f arg=%10.6f %d: abs%10.6f arg=%10.6f'  % \
              (ibot, abs(v[ibot]), atan2(v[ibot].imag,v[ibot].real), \
               itop, abs(v[itop]), atan2(v[itop].imag, v[itop].real))
    for i in range(ny1):
        ileft, irigh = i*(2*nx1-1), i*(2*nx1-1) + nx1 - 1
        print 'W/E %d: abs=%10.6f arg=%10.6f %d: abs%10.6f arg=%10.6f'  % \
              (ileft, abs(v[ileft]), atan2(v[ileft].imag, v[ileft].real), \
               irigh, abs(v[irigh]), atan2(v[irigh].imag, v[irigh].real))



[vabs, varg] = v.AbsArg()

if should_i_plot:
    import ctkplot
    root = Tkinter.Tk() 
    frame = Tkinter.Frame(root) 
    frame.pack() 
    WIDTH, HEIGHT = 300, 300 
    button = Tkinter.Button(frame, text="OK", fg="red", command=frame.quit) 
    button.pack(side=Tkinter.BOTTOM) 
    #canva2 = Tkinter.Canvas(bg="white", width=WIDTH, height=HEIGHT) 
    #canva2.pack() 
    canvas = Tkinter.Canvas(bg="white", width=WIDTH, height=HEIGHT) 
    canvas.pack() 
    tkplot.tkplot(canvas, grid, vabs, 0, 0, 1, WIDTH, HEIGHT) 
    #ctkplot.ctkplot(canvas, grid, v, 0, 0, 1, WIDTH, HEIGHT) 
    #tkplot.tkplot(canva2, grid, F, 0, 0, 1, WIDTH, HEIGHT) 
    #ctkplot.ctkplot(canvas, grid, [], 1, 1, 1, WIDTH, HEIGHT)
    root.mainloop()


