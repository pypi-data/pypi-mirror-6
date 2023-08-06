#!/usr/bin/env python

VERSION = "$Id: doubleGradShafranovDirichlet.py,v 1.6 2010/03/15 21:23:29 pletzer Exp $"

"""
Solve the double boundary problem for the Grad-Shafranov equation
using Dirichlet boundary conditions
"""

from math import pi, cos, sin, sqrt
from Triangulate import Triangulate
from ellipt2d import ellipt2d
import superlu
import Tkinter
import tkplot

class doubleGradShafranov:

    def __init__(self,): pass

    def setContourA(self, pts):
        self.aPts = pts
        
    def setContourAInside(self, pts):
        self.aPtsInterior = pts

    def setContourB(self, pts):
        self.bPts = pts
        
    def setContourBInside(self, pts):
        self.bPtsInterior = pts

    def generateGrid(self, a=0.05):

        ntA = len(self.aPts)
        ntB = len(self.bPts)
                        
        seglist = [ (i, i+1) for i in range(ntA-1) ] \
                  + [ (ntA-1, 0) ] + \
                  [ (ntA+i, ntA+i+1) for i in range(ntB-1) ] \
                   + [ (ntA+ntB-1, ntA) ]

        
        self.midX = 0.5 * (min([p[0] for p in self.aPts]) + \
                           max([p[0] for p in self.aPts]))
        self.midY = 0.5 * (min([p[1] for p in self.aPts]) + \
                           max([p[1] for p in self.aPts]))
        holelist  = [ (self.midX, self.midY) ]

        pts = self.aPts + self.bPts + self.aPtsInterior + self.bPtsInterior
        
        # attributes: -1 on contour a, +1 on contour b
        attlist = [(-1.0,) for i in range(ntA)] 
        attlist += [(+1.0,) for i in range(ntB)]
        attlist += [(0.0,) for i in range(ntA + ntB)] 

        tri = Triangulate()
        tri.set_points(pts)
        tri.set_segments(seglist)
        tri.set_holes(holelist)
        tri.set_attributes(attlist)

        tri.triangulate(area=a, mode='pzq27e')
        self.grid = tri.get_nodes()

        # fill in the list of segments on contour a and b
        self.atts = tri.get_attributes()
        self.segA = []
        self.segB = []
        for e in tri.get_edges():
            ij, m = e
            if m == 1:
                # on some boundary
                i, j = ij
                ai, aj = self.atts[i][0], self.atts[j][0]
                if ai == -1.0 and aj == -1.0:
                    self.segA.append(ij)
                elif ai == +1.0 and aj == +1.0:
                    self.segB.append(ij)
                else:
                    raise("Error: boundary segment that is neither on (a) or (b)")

        f = '(1.0/x)'
        g = '0.0'
        s = None
        self.equ = ellipt2d(self.grid, f, g, s)
        self.A, self.rhs = self.equ.stiffnessMat()

    def setNeumann(self, contour, funct):
        """
        Set Neumann boundary condition
        @param contour 'a' or 'b'
        @param funct function of (x, y)
        """

        # value is dPsi/dn
        # value is > 0 for a gradient pointing outwards

        segs = None
        if contour == 'a':
            segs = self.segA
        elif contour == 'b':
            segs = self.segB

        # assume no Steiner points
        for ij in segs:
            i, j = ij
            xi, yi = self.grid.x(i), self.grid.y(i)
            xj, yj = self.grid.x(j), self.grid.y(j)
            xm     = (xi + xj)/2.0
            ym     = (yi + yj)/2.0
            dx, dy = xj - xi, yj - yi
            ds     = sqrt( dx**2 + dy**2 )
            # the factor x comes from 'f'!
            contrb = xm * funct(xm, ym) * ds /2.
            self.rhs[i] += contrb
            self.rhs[j] += contrb

    def setDirichlet(self, contour, funct):
        """
        Set Dirichlet boundary condition
        @param contour 'a' or 'b'
        @param value
        """
        
        segs = None
        if contour == 'a':
            segs = self.segA
        elif contour == 'b':
            segs = self.segB

        LARGE = 1.2354e8
        
        # assume no Steiner points
        for ij in segs:
            i, j = ij
            x, y = self.grid.x(i), self.grid.y(i)
            self.A[i,i] = LARGE
            self.rhs[i] = funct(x, y) * LARGE

    def solve(self, plot=True):
        """
        Solve
        @param plot plot solution if True
        """
        
        import dsupralu
        import time
        
	m, n = self.A.size()
	handle = dsupralu.new(self.A, n)
	# column permutation
	# 0 natural ordering
	# 1 minimum degree on structure of A'*A
	# 2 minimum degree on structure of A'+A
	# 3 approximate minimum degree for unsymmetric matrices
	cperm = 2
	dsupralu.colperm(handle[0], cperm)
        t0 = time.time()
	dsupralu.lu(handle[0])
        t1 = time.time()
        self.psi = dsupralu.solve(handle[0], self.rhs)
        t2 = time.time()
        print 'Time for LU decomp: %f secs' % (t1 - t0)
        print 'Time for solve    : %f secs' % (t2 - t1)
        #self.psi = superlu.solve(self.A, self.rhs)

        if plot:
            import utils
            utils.toVTK('doubleGradShafranovDirichlet.vtk',
                        cells = self.equ.cells, grid = self.grid,
                        names = ['psi'], fields = [self.psi])
            
            WIDTH = 600
            HEIGHT = 600
            root = Tkinter.Tk()
            frame = Tkinter.Frame(root)
            frame.pack()
            canvas = Tkinter.Canvas(bg="White",width=WIDTH,height=HEIGHT)
            canvas.pack()
            tkplot.tkplot(canvas,self.grid, self.psi, 0,0,1,WIDTH,HEIGHT)
            root.mainloop()
        
    def getPsi(self, contour):
        """
        Get the field
        @param contour 'a' or 'b'
        @return data
        """

        data = []

        segs = None
        if contour == 'a':
            segs = self.segA
        elif contour == 'b':
            segs = self.segB

        for ij in segs:
            i, j = ij
            x, y = self.grid.x(i), self.grid.y(i)
            field = self.psi[i]
            data.append(field)

        return data

    def getDPsi(self, contour):
        """
        Get the normal derivative of field
        @param contour 'a' or 'b'
        @return data
        """

        data = []
        ptsIn = []
        ptsOut = []
        iInBeg = 0
        iOutBeg = 0
        na = len(self.aPts)
        nb = len(self.bPts)
        segs = None
        if contour == 'a':
            ptsIn = self.aPtsInterior
            iInBeg = na + nb
            ptsOut = self.aPts
            iOutBeg = 0
        elif contour == 'b':
            ptsIn = self.bPtsInterior
            iInBeg = na + nb + na
            ptsOut = self.bPts
            iOutBeg = na

        for i in range(len(ptsIn)):
            xIn, yIn = ptsIn[i]
            iIn = iInBeg + i
            xOut, yOut = ptsOut[i]
            iOut = iOutBeg + i
            assert(abs(self.atts[iOut][0]) - 1.0 < 1.e-6) # make sure it is on a boundary
            distance = sqrt( (xOut - xIn)**2 + (yOut - yIn)**2 )
            data.append( (self.psi[iOut] - self.psi[iIn]) / distance ) 

        return data

    
    
##############################################################################

def printStat(header, data):
    minV = float('inf')
    maxV = -float('inf')
    avrg = 0.0
    for d in data:
        minV = min(minV, d)
        maxV = max(maxV, d)
        avrg += d
    avrg /= float(len(data))
    print header, ' avg/min/max: %f %f %f' % (avrg, minV, maxV)
    
def main():
    from optparse import OptionParser
    import sys
    from math import cos, sin, pi, atan2
    import gLaplaceN

    parser = OptionParser(version=VERSION)
    
    parser.add_option('-i', '--input', action='store', type="string",
                      dest="inputFile", help="input file",
                      default="")
    parser.add_option('-A', '--Area', action='store', type="float",
                      dest="area", help="largest triangle area",
                      default=0.0001)
    parser.add_option('-e', '--epsilon', action='store', type="float",
                      dest="epsilon",
                      help="small, norm. dist. from boundary used to estimate d/dn (0.01)",
                      default=0.01)
    parser.add_option('-R', '--R0', action='store', type="float",
                      dest="R0", help="Major radius (>0)",
                      default=1.0)
    parser.add_option('-a', '--aMinor', action='store', type="float",
                      dest="aMinor", help="Inner minor radius (> 0)",
                      default=0.5)
    parser.add_option('-b', '--bMinor', action='store', type="float",
                      dest="bMinor", help="Outer minor radius (> a)",
                      default=0.9)
    parser.add_option('-t', '--theta', action='store', type="int",
                      dest="theta", help="Number of inner theta points",
                      default=128)
    parser.add_option('-E', '--Elongation', action='store', type="float",
                      dest="kappa", help="Elongation (> 0)",
                      default=1.0)
    parser.add_option('-T', '--Triangularity', action='store', type="float",
                      dest="delta", help="Triangularity",
                      default=0.0)
    parser.add_option('-p', '--plot', action='store_true',
                      dest="plot", help="To plot solution",
                      default=False)

    options, args = parser.parse_args(sys.argv)

    epsilon = options.epsilon
    onePlusEps = 1.0 + epsilon
    oneMinusEps = 1.0 - epsilon

    print """
%s called with options %s
    """ % (sys.argv[0], str(sys.argv[1:]))

    ptsA = []
    ptsB = []
    ptsAIn = [] # epsilon in of ptsA
    ptsBIn = [] # epsilon in of ptsB

    if not options.inputFile:
        
        R0 = options.R0
        a = options.aMinor
        b = options.bMinor
        kappa = options.kappa
        delta = options.delta
        print """
R0 = %f
a = %f
b = %f
kappa = %f
delta = %f
""" % (R0, a, b, kappa, delta)

        ntA = options.theta
        dtA = 2*pi/float(ntA)
        ptsA = [(R0 + a*cos(i*dtA + delta*sin(i*dtA)), kappa*a*sin(i*dtA)) \
                for i in range(ntA)]
        ptsAIn = [(R0 + a*onePlusEps*cos(i*dtA + delta*sin(i*dtA)), kappa*a*onePlusEps*sin(i*dtA)) \
                for i in range(ntA)]
        ntB = int( (b/a) * ntA )
        dtB = 2*pi/float(ntB)
        ptsB = [(R0 + b*cos(i*dtB + delta*sin(i*dtB)), kappa*b*sin(i*dtB)) \
                for i in range(ntB)]
        ptsBIn = [(R0 + b*oneMinusEps*cos(i*dtB + delta*sin(i*dtB)), kappa*b*oneMinusEps*sin(i*dtB)) \
                for i in range(ntB)]

    else:
        # read contours from input file
        print """
%s called with options %s
    """ % \
        (sys.argv[0], str(sys.argv[1:]),)
        import grInput
        gi = grInput.Input()
        gi.open(filename = options.inputFile)
        
        ptsA = gi.getContour1()
        ntA = len(ptsA)
        ptsB = gi.getContour2()
        ntB = len(ptsB)

        # fill in interior nodes used to compute the normal derivative
        r0 = reduce(lambda x,y: x+y, [p[0] for p in ptsA]) / float(ntA)
        z0 = reduce(lambda x,y: x+y, [p[1] for p in ptsA]) / float(ntA)
        
        for i in range(ntA):
            j = (i + 1) % ntA
            xi, yi = ptsA[i]
            xj, yj = ptsA[j]
            dx = xj - xi
            dy = yj - yi
            ds = sqrt(dx**2 + dy**2)
            xm = 0.5 * (xi + xj)
            ym = 0.5 * (yi + yj)
            det = (xm - r0)*dy - (ym - z0)*dx
            sgn = det / abs(det)
            nx = + sgn * dy/ds
            ny = - sgn * dx/ds
            ptsAIn.append( (xm + nx*epsilon*r0, ym + ny*epsilon*r0) )
            
        for i in range(ntB):
            j = (i + 1) % ntB
            xi, yi = ptsB[i]
            xj, yj = ptsB[j]
            dx = xj - xi
            dy = yj - yi
            ds = sqrt(dx**2 + dy**2)
            xm = 0.5 * (xi + xj)
            ym = 0.5 * (yi + yj)
            det = (xm - r0)*dy - (ym - z0)*dx
            sgn = det / abs(det)
            nx = + sgn * dy/ds
            ny = - sgn * dx/ds
            ptsBIn.append( (xm - nx*epsilon*r0, ym - ny*epsilon*r0) )

    dl = doubleGradShafranov()
    dl.setContourA(ptsA)
    dl.setContourAInside(ptsAIn)
    dl.setContourB(ptsB)
    dl.setContourBInside(ptsBIn)
    
    dl.generateGrid(a = options.area)

    gr = gLaplaceN.Green(nTor=1)

    xSource, ySource = dl.midX, dl.midY
    
    def dirichletDiracSource(x, y):
        gr.set(x, y, xSource, ySource)
        return x * xSource * gr.get()
    
    # normal pointing inwards
    dl.setDirichlet('a', dirichletDiracSource)
    dl.setDirichlet('b', dirichletDiracSource)
    
    dl.solve(plot=options.plot)

    psiA = dl.getPsi('a')
    psiB = dl.getPsi('b')

    dPsiA = dl.getDPsi('a')
    dPsiB = dl.getDPsi('b')

    printStat('psi on (a): ', psiA)
    printStat('psi on (b): ', psiB)
    print

    # exact values
    dPsiAExact = []
    for ij in dl.segA:
        i, j = ij
        xi, yi = dl.grid.x(i), dl.grid.y(i)
        xj, yj = dl.grid.x(j), dl.grid.y(j)
        xm = 0.5 * (xi + xj)
        ym = 0.5 * (yi + yj)
        gr.set(xm, ym, xSource, ySource)
        dx = xj - xi
        dy = yj - yi
        ds = sqrt(dx**2 + dy**2)
        val = xSource*(+ dy*(gr.get() + xm*gr.getDx1()) - dx*gr.getDy1()) / ds
        dPsiAExact.append(val)
##         x, y = dl.grid.x(i), dl.grid.y(i)
##         th = atan2(y - ySource, x - xSource)
##         xDthNorm = -b*sin(th + delta*sin(th)) * (1.0 + delta*cos(th))
##         yDthNorm = +kappa*b*cos(th)
##         norm = sqrt(xDthNorm**2 + yDthNorm**2)
##         xDthNorm /= norm
##         yDthNorm /= norm
##         gr.set(x, y, xSource, ySource)
##         dPsiAExact.append(-yDthNorm*xSource*(gr.get() + x*gr.getDx1()) + \
##                           xDthNorm*x*xSource*gr.getDy1())
        
    dPsiBExact = []
    for ij in dl.segB:
        i, j = ij
        xi, yi = dl.grid.x(i), dl.grid.y(i)
        xj, yj = dl.grid.x(j), dl.grid.y(j)
        xm = 0.5 * (xi + xj)
        ym = 0.5 * (yi + yj)
        gr.set(xm, ym, xSource, ySource)
        dx = xj - xi
        dy = yj - yi
        ds = sqrt(dx**2 + dy**2)
        val = xSource*(+ dy*(gr.get() + xm*gr.getDx1()) - dx*gr.getDy1()) / ds
        dPsiBExact.append(val)
        
##         x, y = dl.grid.x(i), dl.grid.y(i)
##         th = atan2(y - ySource, x - xSource)
##         xDthNorm = -b*sin(th + delta*sin(th)) * (1.0 + delta*cos(th))
##         yDthNorm = +kappa*b*cos(th)
##         norm = sqrt(xDthNorm**2 + yDthNorm**2)
##         xDthNorm /= norm
##         yDthNorm /= norm
##         gr.set(x, y, xSource, ySource)
##         dPsiBExact.append(yDthNorm*xSource*(gr.get() + x*gr.getDx1()) - \
##                           xDthNorm*x*xSource*gr.getDy1())
            

if __name__ == '__main__': main()
