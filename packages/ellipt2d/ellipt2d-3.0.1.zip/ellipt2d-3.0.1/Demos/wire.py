#!/usr/bin/env python

# $Id: wire.py,v 1.13 2013/12/20 17:17:07 pletzer Exp $

"""
Resonant frequencies of a lattice with central concavity
"""

from math import pi, cos, sin
from cellipt2d import ellipt2d
import Ireg2tri, time, ctkplot, cmath, csuperlu, cvector

TWOPI = 2.*pi

class wire:

    """
    Purpose: Solve the eigenvalue Helmholtz equation in a square with a
    central concavity. The boundary conditions are a phase shift between
    south and north, and east and west. On the segments of the concavity
    zero Dirichlet boundary conditions are applied.

    Method: the eigenvalue problem is solved by inverse iterations.
    """

    def __init__(self):

        # the box size
        self.L = TWOPI

        # no of elements on exterior edges
        self.n1 = 21

        # Max cell area
        self.area = self.L**2/self.n1**2

        # Coordinates of concavity (the wire)
        self.xc, self.yc = self.L/2., self.L/2.
        # Concavity radius (wire radius)
        self.radius = self.L/5.
        # No of points defining the concavity
        self.nt = self.n1-1

        # Boundary conditions phase shifts
        # solution(north) = exp(j*ky*L) solution(south)
        self.kx, self.ky = 0.* TWOPI/self.L, 0.* TWOPI/self.L

    def genmesh(self, nrefine):

        """
        Generate the mesh and refine (nrefine>=0)
        """
        nx1 = ny1 = self.n1
        L = self.L
        nt = self.nt
        xy=[]
        seglist = []
        holelist = []
        nx, ny = nx1-1, ny1-1
        dx, dy = L/nx, L/ny

        # south
        for i in range(nx):
            x, y = i*dx, 0.
            xy.append((x, y))

        # east
        for i in range(ny):
            x, y = L, i*dy
            xy.append((x, y))

        # north
        for i in range(nx):
            x, y = L-i*dx, L
            xy.append((x, y))

        # west
        for i in range(ny):
            x, y = 0., L-i*dy
            xy.append((x, y))

        # connect points
        for i in range(len(xy)-1):
            seglist.append((i,i+1))
        seglist.append((len(xy)-1, 0))

        # circular concavity
        dt = 2*pi/nt
        js = len(seglist)
        self.npts = len(xy)
        for i in range(nt):
            t = i*dt + pi/4
            x, y = self.xc + self.radius*cos(t), self.yc + self.radius*sin(t)
            xy.append((x, y))

        for i in range(nt-1):
            seglist.append((js+i,js+i+1))
        seglist.append((js+nt-1, js))

        # one hole
        holelist.append((self.xc, self.yc))

        meshgen = Ireg2tri.Ireg2tri(self.area)

        meshgen.setUpConvexHull(xy, seglist, [], holelist)
        meshgen.triangulate()

        self.grid = meshgen.refine(nrefine)
        self.N = len(self.grid)

    def assemble(self):

        "Assemble matrices A (=stiffness) and B"

        nx1=ny1=self.n1
        nx, ny = nx1-1, ny1-1

        self.stiff = ellipt2d(self.grid, '1.', None, None)
        [self.amat, rhs] = self.stiff.stiffnessMat()

        lump = ellipt2d(self.grid, None, '1.', None)
        [self.bmat, rhs] = lump.stiffnessMat()


        ## apply phase shifted BCs on the exterior ##
        cx, cy = cmath.exp(1j*self.kx*self.L), cmath.exp(1j*self.ky*self.L)

        # south/north
        for i in range(1, nx):
            js, jn = i, 2*nx+ny-i
            ass, ann = self.amat[(js,js)], self.amat[(jn,jn)]
            self.amat[(js,js)] += ann
            self.amat[(jn,jn)] += ass
            bss, bnn = self.bmat[(js,js)], self.bmat[(jn,jn)]
            self.bmat[(js,js)] += bnn
            self.bmat[(jn,jn)] += bss
            neighbors = self.grid[jn][1]
            for j in neighbors:
                self.amat[(js, j)] = self.amat[(jn, j)] / cy
                self.bmat[(js, j)] = self.bmat[(jn, j)] / cy
            neighbors = self.grid[js][1]
            for j in neighbors:
                self.amat[(jn, j)] = self.amat[(js, j)] * cy
                self.bmat[(jn, j)] = self.bmat[(js, j)] * cy

        # east/west
        for i in range(1, ny):
            je, jw = nx+i, 2*nx+2*ny-i
            aee, aww = self.amat[(je,je)], self.amat[(jw,jw)]
            self.amat[(je,je)] += aww
            self.amat[(jw,jw)] += aee
            bee, bww = self.bmat[(je,je)], self.bmat[(jw,jw)]
            self.bmat[(je,je)] += bww
            self.bmat[(jw,jw)] += bee
            neighbors = self.grid[jw][1]
            for j in neighbors:
                self.amat[(je, j)] = self.amat[(jw, j)] * cx
                self.bmat[(je, j)] = self.bmat[(jw, j)] * cx
            neighbors = self.grid[je][1]
            for j in neighbors:
                self.amat[(jw, j)] = self.amat[(je, j)] / cx
                self.bmat[(jw, j)] = self.bmat[(je, j)] / cx


        # corners sw, se, ne, nw
        isw, ise, ine, inw = 0, nx, nx+ny, 2*nx+ny
        self.amat[(isw,isw)] += self.amat[(ise,ise)] + self.amat[(ine,ine)] + self.amat[(inw,inw)]
        self.amat[(ise,ise)] = self.amat[(isw,isw)]
        self.amat[(ine,ine)] = self.amat[(isw,isw)]
        self.amat[(inw,inw)] = self.amat[(isw,isw)]
        #
        self.bmat[(isw,isw)] += self.bmat[(ise,ise)] + self.bmat[(ine,ine)] + self.bmat[(inw,inw)]
        self.bmat[(ise,ise)] = self.bmat[(isw,isw)]
        self.bmat[(ine,ine)] = self.bmat[(isw,isw)]
        self.bmat[(inw,inw)] = self.bmat[(isw,isw)]

        neighbors = self.grid[isw][1]
        for j in neighbors:
            self.amat[(ise,j)] = self.amat[(isw,j)] * cx
            self.amat[(ine,j)] = self.amat[(isw,j)] * cx * cy
            self.amat[(inw,j)] = self.amat[(isw,j)] * cy
            #
            self.bmat[(ise,j)] = self.bmat[(isw,j)] * cx
            self.bmat[(ine,j)] = self.bmat[(isw,j)] * cx * cy
            self.bmat[(inw,j)] = self.bmat[(isw,j)] * cy

        neighbors = self.grid[ise][1]
        for j in neighbors:
            self.amat[(isw,j)] = self.amat[(ise,j)] / cx
            self.amat[(ine,j)] = self.amat[(ise,j)] * cy
            self.amat[(inw,j)] = self.amat[(ise,j)] * cy / cx
            #
            self.bmat[(isw,j)] = self.bmat[(ise,j)] / cx
            self.bmat[(ine,j)] = self.bmat[(ise,j)] * cy
            self.bmat[(inw,j)] = self.bmat[(ise,j)] * cy / cx

        neighbors = self.grid[ine][1]
        for j in neighbors:
            self.amat[(isw,j)] = self.amat[(ine,j)] / cx / cy
            self.amat[(ise,j)] = self.amat[(ine,j)] / cy
            self.amat[(inw,j)] = self.amat[(ine,j)] / cx
            #
            self.bmat[(isw,j)] = self.bmat[(ine,j)] / cx / cy
            self.bmat[(ise,j)] = self.bmat[(ine,j)] / cy
            self.bmat[(inw,j)] = self.bmat[(ine,j)] / cx

        neighbors = self.grid[inw][1]
        for j in neighbors:
            self.amat[(isw,j)] = self.amat[(inw,j)] / cy
            self.amat[(ise,j)] = self.amat[(inw,j)] * cx / cy
            self.amat[(ine,j)] = self.amat[(inw,j)] * cx
            #
            self.bmat[(isw,j)] = self.bmat[(inw,j)] / cy
            self.bmat[(ise,j)] = self.bmat[(inw,j)] * cx / cy
            self.bmat[(ine,j)] = self.bmat[(inw,j)] * cx


        ## apply zero Dirichlet BCs in the interior by hand ##
        huge = 1.e6
        for i in range(self.npts, self.npts+self.nt):
            for j in self.grid.data[i][1]:
                del self.amat[(i,j)] #= 0.0
            self.amat[(i,i)] = huge


    def solve(self, lambda0=0.0, tol=1.e-6, niter=10):

        """
        Solve eigensystem:
        lambda0 = inital eigenvalue guess
        tol     = tolerance in eigenvalue
        niter   = max number of inverse iterations
        """
        
        self.v = cvector.random(self.N, 0., 1.+0j) # initial guess
        for i in range(self.N):
            x, y = self.grid.x(i), self.grid.y(i)
            self.v[i] = cos(self.kx*x)*cos(self.ky*y) +0j

        tol = 1.e-6
        niter = 10
        [self.lambd, self.v, residue, iter] = csuperlu.eigen(\
            self.amat, self.bmat, lambda0, self.v, tol, niter)

    def tkplot(self):
        
        try:
            from tkinter import Tk, Frame, Button, Canvas, BOTTOM
        except:
            from Tkinter import Tk, Frame, Button, Canvas, BOTTOM
        import tkplot

        root = Tk() 
        frame = Frame(root) 
        frame.pack() 
        width, height = 500, 450 
        button = Button(frame, text="OK", fg="red", command=frame.quit) 
        button.pack(side=BOTTOM) 
        canvas = Canvas(bg="white", width=width, height=height) 
        canvas.pack()
        title=None
        try:
            title = "%f"%self.lambd.real
        except:
            title = "%f"%self.lambd
        ctkplot.ctkplot(canvas, self.grid, self.v, 0,0,1,
                        title=title, WIDTH=width, HEIGHT=height) 
        root.mainloop() 

#........................................................................
if __name__ == '__main__':
    import sys

    s = wire()
    s.radius = 0.1*s.L
    s.kx, s.ky = 0.2, 0.1
    s.genmesh(nrefine=0)
    print('No of nodes = ', s.N)
    s.assemble()

    # compute dispersion relation
    print('lambda\t\tDeterminant')
    import zsupralu
    lam_min = 0.18
    lam_max = 0.19
    nlam = 11
    dlam = (lam_max - lam_min)/nlam
    for i in range(nlam):
        lam = lam_min + dlam*i
        cmat = s.amat - lam*s.bmat
        h = zsupralu.new(cmat, cmat.size()[0])
        permc = 2
        zsupralu.colperm(h[0], permc)
        zsupralu.lu(h[0])
        dets = zsupralu.det(h[0])
        print('%f\t(%f+i*%f)* 2**%d' %\
              (lam, \
               dets[0].real,dets[0].imag, \
               dets[1]))
        
    lam0 = 0.1*TWOPI**2/s.L**2
    if len(sys.argv)>1:
        lam0 = float(sys.argv[1])*TWOPI**2/s.L**2
    s.solve(lambda0=lam0)
    s.tkplot()
