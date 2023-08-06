#!/usr/bin/env python

"""
Grad-Shafranov solver
"""

from math import *
from ellipt2d import *
import Ireg2tri, time, ctkplot, superlu

TWOPI = 2.*pi

def flux_function(s, value_mag=1.0, value_edge=0.0, alpha=1):
    " s = (psi - psi_mag)/(psi_edge-psi_mag) "
    return value_edge + value_mag*(1.0 - s**alpha)


def is_in_plasma(x, y, xy):
    """
    return 0 if outside,
    1 if likely inside
    2 if most likely inside
    3 if almost cetainly inside
    """
    
    res = 0
    tol = (0.1, 0.01, 0.001)
    angle = 0.0
    for i in range(len(xy)-1):
        xb1, yb1 = xy[i  ][0], xy[i  ][1]
        xb2, yb2 = xy[i+1][0], xy[i+1][1]
        cross    = (xb1-x)*(yb2-y) - (yb1-y)*(xb2-x)
        dot      = (xb1-x)*(xb2-x) + (yb1-y)*(yb2-y)
        angle   += abs(atan2(cross, dot))
    diff = abs(angle - 2*pi)
    return reduce(lambda x,y:x+y, map(lambda x: diff<x, tol))
        

def boundary_points(xy, seglist, nt, r0, radius,
                    kappas=(1.0,1.0), deltas=(0.0,0.0)):
    
    """
    Compute x, y boundary points
    kappas: upper/lower elongation
    deltas: upper/lower triangularity
    """
    
    dt = TWOPI/nt
    js = len(seglist)

    for i in range(0, nt/2):
        t = i*dt
        x, y = r0 + radius*cos(t + deltas[0]*sin(t)), kappas[0]*radius*sin(t)
        xy.append((x, y))
    for i in range(nt/2+1, nt):
        t = i*dt
        x, y = r0 + radius*cos(t + deltas[1]*sin(t)), kappas[1]*radius*sin(t)
        xy.append((x, y))

##    for i in range(nt-1):
##        seglist.append((js+i,js+i+1))
##    seglist.append((js+nt-1, js))


class gs:

    def __init__(self):

        # profiles
        self.pp0 = +10000.0
        self.ggp0 = 1.5


        # boundary shape
        self.r0 = 1.0
        self.a = 0.8
        self.kappas = (1.2, 2.0)
        self.deltas = (0.3, 1.5)
        self.nt1 = 81

        # box size and resolution
        self.b_over_a = 1.2 # b/a ratio
        self.nx1 = 21
        self.ny1 = int((self.kappas[0]+self.kappas[1])*self.nx1/2.)
        

        # triangulation resolution 
        self.area = 0.01
    
    def genmesh(self, nrefine=0):

        xmin = max(0.1*self.r0, self.r0 - self.a*self.b_over_a)
        xmax = self.r0 + self.a*self.b_over_a
        ymin = - self.a*self.kappas[1]* self.b_over_a
        ymax = + self.a*self.kappas[0]* self.b_over_a

        xy=[]
        seglist = []
        holelist = []
        
        # start by distributing points regularly and uniformly in the box
        # we will use the field values on these points to build the uniform
        # field.
        nx1 = self.nx1
        ny1 = self.ny1
        nx, ny = nx1-1, ny1-1
        dx  = (xmax - xmin)/nx
        dy  = (ymax - ymin)/ny
        for j in range(ny1):
            y = ymin + j*dy
            xy += [(xmin+i*dx, y) for i in range(nx1)]

        for i in range(nx):
            seglist.append((i, i+1)) # south
            seglist.append((ny*nx1+i, ny*nx1+i+1)) # north
        for j in range(ny):
            seglist.append((j*nx1, (j+1)*nx1))       # west
            seglist.append((j*nx1+nx, (j+1)*nx1+nx)) # east
            
        self.nbound_start = len(xy)
        nseg_start = len(seglist)
        
        # plasma boundary
        nt = self.nt1 - 1
        boundary_points(xy, seglist, nt, self.r0, self.a,
                        self.kappas, self.deltas)
        self.seg_bound = seglist[nseg_start:]
        self.xy_bound = xy[self.nbound_start:] + [xy[self.nbound_start]]

        self.nbound_end = len(xy)

        meshgen = Ireg2tri.Ireg2tri(self.area)
        meshgen.mode = 'zepq15' # 'zeq27'
        meshgen.setUpConvexHull(xy, seglist, [], holelist)
        meshgen.triangulate()

        self.grid = meshgen.refine(nrefine)
        self.N = len(self.grid)

        #self.grid.plot()
        
        # initial guess
        self.psi  = vector.zeros(len(self.grid))
        self.psi_mag = min(self.psi)
        self.psi_edge= 0.0 # by definition

    def iterate(self):

        "Solve..."

        ffun, gfun = '1.0/x', '0'
        # source term
        self.jphi = vector.zeros(len(self.grid))
        for i in range(self.N):
            x, y = self.grid.x(i), self.grid.y(i)
            if is_in_plasma(x, y, self.xy_bound) >= 1: 
                psi  = self.psi[i]
                try:
                    s    = (psi-self.psi_mag)/(self.psi_edge-self.psi_mag)
                except:
                    s = 0.5
                pp = flux_function(s,
                                   value_mag=self.pp0, value_edge=0.0,
                                   alpha = 1)
                ggp= flux_function(s,
                                   value_mag=self.ggp0, value_edge=0.0,
                                   alpha = 2)
                self.jphi[i] = -x*pp - ggp/x

        self.equ = ellipt2d(self.grid, ffun, gfun, self.jphi)
        [self.amat, self.rhs] = self.equ.stiffnessMat()
        
        # zero Neumann BCs on box boundary=> no need to modify A and B
        # Dirichlet on plasma layer
        huge = 1.23946e8
        for i in range(self.nbound_start, self.nbound_end):
            self.amat[(i,i)] = huge

        # now solve
        self.psi = superlu.solve(self.amat, self.rhs)
        psi_mag_new = min(self.psi)
        diff_psimag = abs(psi_mag_new - self.psi_mag)
        self.psi_mag = psi_mag_new
        return diff_psimag

    def tkplot(self):
        
        from Tkinter import Tk, Frame, Button, Canvas, BOTTOM, LEFT
        import tkplot
        root = Tk() 
        frame = Frame(root) 
        frame.pack()
        width = 300
        height = (self.kappas[0]+self.kappas[1])*width/2.0
        button = Button(frame, text="OK", fg="red", command=frame.quit) 
        button.pack(side=BOTTOM) 
        canvas = Canvas(bg="white", width=width, height=height) 
        canvas.pack(side=LEFT)
##        inside = [0.0 for i in range(self.N)]
##        for i in range(self.N):
##            x, y = self.grid.x(i), self.grid.y(i)
##            inside[i] = is_in_plasma(x, y, self.xy_bound)
        tkplot.tkplot(canvas, self.grid, self.jphi,
                      draw_mesh=1, node_no=0, add_minmax=1,
                      title="j_phi", WIDTH=width, HEIGHT=height) 
        canvas2 = Canvas(bg="white", width=width, height=height) 
        canvas2.pack(side=LEFT)
        tkplot.tkplot(canvas2, self.grid, self.psi,
                      draw_mesh=1, node_no=0, add_minmax=1,
                      title="psi", WIDTH=width, HEIGHT=height) 
        root.mainloop() 


#................................................................................
if __name__ == '__main__':
    g = gs()
    g.genmesh()
    print 'No of nodes = ', g.N
    rtol = 0.001
    error = 100.0
    niter = 10
    iter = 1
    while error>rtol and iter<niter:
        error = abs(g.iterate()/g.psi_mag)
        print 'iter=%d error->%g psi_mag=%g ' % (iter, error, g.psi_mag)
        iter += 1
    g.tkplot()
