#!/usr/bin/env python
# $Id: gradshafranov.py,v 1.4 2013/12/20 17:17:07 pletzer Exp $
"""
Grad-Shafranov 
"""

from math import *
from ellipt2d import *
import Ireg2tri, time, ctkplot, superlu

TWOPI = 2.*pi

def circle_points(xy, seglist, nt, r0, radius, kappa=1.0, delta=0.):
    " spread points around circle "
    dt = TWOPI/nt
    js = len(seglist)

    for i in range(nt):
        t = i*dt + pi/42*pi*0.3*0.06 *9/2.
        x, y = r0 + radius*cos(t + delta*sin(t)), kappa*radius*sin(t)
        xy.append((x, y))

    for i in range(nt-1):
        seglist.append((js+i,js+i+1))
    seglist.append((js+nt-1, js))
    

class gs:

    """
    Purpose: Solve the Grad-Shafranov equation in a rectangular domain
    with central Dirac-like current and a boundary layer current.
    """

    def __init__(self):

        # boundary layer position and shape
        self.r0 = 1.0
        self.a = 0.3
        self.kappa = 1.7
        self.delta = 1.0
        self.rm = self.r0 + 0.4*(self.a) # magnetic axis
        self.eps = 0.1 * self.a # thickness of layer

        self.n1 = 21

        # plasma current
        self.Ip = 1.0

        self.area = 0.001


    def genmesh(self, nrefine):

        """
        Generate the mesh and refine (nrefine>=0)
        """
        max_radius = self.a + self.eps
        # the box coordinates (xmin, xmax, ymin, ymax)
        self.box = (0.95*(self.r0-max_radius),
                    1.02*(self.r0+max_radius),
                    -1.02*max_radius*self.kappa, 1.02*max_radius*self.kappa)

        nx1 = ny1 = self.n1
        x0, y0 = self.box[0], self.box[2]
        xn, yn = self.box[1], self.box[3]
        Lx = xn - x0
        Ly = yn - y0

        self.nt = int(TWOPI/self.eps)
        nt = self.nt
        print ' will use nt = ', nt,' circle points'
        
        xy=[]
        seglist = []
        regionlist = []
        holelist = []
        nx, ny = nx1-1, ny1-1
        dx, dy = Lx/nx, Ly/ny

        # south
        for i in range(nx):
            x, y = x0 + i*dx, y0
            xy.append((x, y))

        # east
        for i in range(ny):
            x, y = xn, y0 + i*dy
            xy.append((x, y))

        # north
        for i in range(nx):
            x, y = xn - i*dx, yn
            xy.append((x, y))

        # west
        for i in range(ny):
            x, y = x0, yn - i*dy
            xy.append((x, y))

        # connect points
        for i in range(len(xy)-1):
            seglist.append((i,i+1))
        seglist.append((len(xy)-1, 0))

        # circular plasma
        self.npts = len(xy)

##        radius = self.a*(1 - self.eps)
##        circle_points(xy, seglist, nt, self.r0, radius)
        radius = self.a
        self.index_circle0 = len(xy)
        circle_points(xy, seglist, nt, self.r0, self.a, self.kappa, self.delta)
        self.index_circlen = len(xy)
##        radius = self.a*(1 + self.eps)
##        circle_points(xy, seglist, nt, self.r0, radius)

        # center
        self.rad_inner = self.eps
        radius = self.rad_inner
        self.nt_inner = int( self.nt*self.eps/self.a )
        circle_points(xy, seglist, self.nt_inner, self.rm, radius)

        self.index_center = len(xy)
        x, y = self.rm, 0.
        xy.append((x, y))

##        # one hole
##        holelist.append((self.xc, self.yc))

        meshgen = Ireg2tri.Ireg2tri(self.area)

        meshgen.setUpConvexHull(xy, seglist, regionlist, holelist)
        meshgen.triangulate()

        self.grid = meshgen.refine(nrefine)
        self.N = len(self.grid)

        #self.grid.plot()

    def assemble(self):

        "Assemble matrices A (=stiffness) and B"

        nx1=ny1=self.n1
        nx, ny = nx1-1, ny1-1

        ffun, gfun = '1.0/x', '0'

        # source term
        self.jphi = vector.zeros(len(self.grid))
        
        # add source contribution in boundary layer        
        area = TWOPI*self.a*2.*(self.eps)/4.        
##        for i in range(self.index_circle0, self.index_circlen):
##            self.jphi[i] = - self.Ip/(area)
            
        # plasma current in center
        # effective area
        area = math.pi * self.rad_inner**2 / 4.
        self.jphi[self.index_center] = self.Ip / area
        
        
        self.equ = ellipt2d(self.grid, ffun, gfun, self.jphi)
        [self.amat, self.rhs] = self.equ.stiffnessMat()

        # zero Neumann BCs on box boundary=> no need to modify A and B
        # Dirichlet on plasma layer
        huge = 1.23946e6
        for i in range(self.index_circle0, self.index_circlen):
            self.amat[(i,i)] = huge


    def solve(self):

        """
        Solve A x = b
        tol     = tolerance in eigenvalue
        """
        
        self.v = superlu.solve(self.amat, self.rhs)

    def tkplot(self):
        
        from Tkinter import Tk, Frame, Button, Canvas, BOTTOM
        import tkplot
        root = Tk() 
        frame = Frame(root) 
        frame.pack() 
        WIDTH, HEIGHT = 500, 450 
        button = Button(frame, text="OK", fg="red", command=frame.quit) 
        button.pack(side=BOTTOM) 
        canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT) 
        canvas.pack()
        v = self.v
        tkplot.tkplot(canvas, self.grid, v, 1,0,1, WIDTH, HEIGHT) 
        root.mainloop() 

#........................................................................
if __name__ == '__main__':

    s = gs()
    s.r0, s.a  = 1., 0.3
    s.genmesh(nrefine=1)
    print 'No of nodes = ', s.N
    s.assemble()
    s.solve()
    s.tkplot()
