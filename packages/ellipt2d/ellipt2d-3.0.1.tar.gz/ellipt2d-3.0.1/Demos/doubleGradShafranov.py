#!/usr/bin/env python

VERSION = "$Id: doubleGradShafranov.py,v 1.13 2010/03/15 21:23:25 pletzer Exp $"

"""
Solve the double boundary problem for the Grad-Shafranov equation using a regularization
transformation and Neumann boundary conditions

"""

from math import pi, cos, sin, sqrt, atan2
from Triangulate import Triangulate
from ellipt2d import ellipt2d
import superlu
import Tkinter
import tkplot

class doubleGradShafranov:

    def __init__(self,): pass

    def setContourA(self, pts):
        self.ptsA = pts

    def setContourB(self, pts):
        self.ptsB = pts

    def generateGrid(self, a=0.05):

        pts = self.ptsA + self.ptsB
        ntA = len(self.ptsA)
        ntB = len(self.ptsB)

        # attributes: -1 on contour a, +1 on contour b
        attlist = [(-1.0,) for i in range(ntA)]
        attlist += [(+1.0,) for i in range(ntB)]
                
        seglist = [ (i, i+1) for i in range(ntA-1) ] \
                  + [ (ntA-1, 0) ]
        seglist += [ (ntA+i, ntA+i+1) for i in range(ntB-1) ] \
                   + [ (ntA+ntB-1, ntA) ]

        self.midX = 0.5 * (min([p[0] for p in self.ptsA]) + \
                           max([p[0] for p in self.ptsA]))
        self.midY = 0.5 * (min([p[1] for p in self.ptsA]) + \
                           max([p[1] for p in self.ptsA]))
        holelist  = [ (self.midX, self.midY) ]
        
        tri = Triangulate()
        tri.set_points(pts)
        tri.set_segments(seglist)
        tri.set_holes(holelist)
        tri.set_attributes(attlist)

        tri.triangulate(area=a, mode='pzq27e')
        self.grid = tri.get_nodes()

        # fill in the list of segments on contour a and b
        atts = tri.get_attributes()
        self.segA = []
        self.segB = []
        for e in tri.get_edges():
            ij, m = e
            if m == 1:
                # on some boundary
                i, j = ij
                ai, aj = atts[i][0], atts[j][0]
                if ai == -1.0 and aj == -1.0:
                    self.segA.append(ij)
                elif ai == +1.0 and aj == +1.0:
                    self.segB.append(ij)
                else:
                    raise("Error: boundary segment that is neither on (a) or (b)")

        f = 'x'
        g = '1.0/x'
        s = None
        self.equ = ellipt2d(self.grid, f, g, s)
        self.A, self.rhs = self.equ.stiffnessMat()

    def setNeumann(self, contour, funct):
        """
        Set Neumann boundary condition
        @param contour 'a' or 'b'
        @param funct function of (xi, yi, xj, yj)
        """

        # value is dChi/dn
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
            contrb = xm * funct(xi, yi, xj, yj) * ds /2.
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
        
        self.chi = dsupralu.solve(handle[0], self.rhs)
        t2 = time.time()
        print 'Time for LU decomp: %f secs' % (t1 - t0)
        print 'Time for solve    : %f secs' % (t2 - t1)

        #self.chi = superlu.solve(self.A, self.rhs)
        self.psi = [self.grid.x(i) * self.chi[i] for i in range(len(self.chi))]

        if plot:
            import utils
            utils.toVTK('doubleGradShafranov.vtk',
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
        
    def getChi(self, contour):
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
            field = self.chi[i]
            data.append(field)

        return data

    def getXY(self, contour):
        """
        Get coordinates along given contour
        @param contour 'a' or 'b
        @return (xs, ys) coordinates
        """
        data = []
        segs = None
        if contour == 'a':
            segs = self.segA
        elif contour == 'b':
            segs = self.segB

        xData, yData = [], []
        for ij in segs:
            i, j = ij
            x, y = self.grid.x(i), self.grid.y(i)
            xData.append(x)
            yData.append(y)

        return xData, yData

    def getNormalDerivativeOperator(self, contour):
        """
        Get the normal derivative operator along given contour
        @param contour 'a' or 'b
        @return (nx, ny) with normal derivative
                         d/dn = nx*d/dx + ny*d/dy defined on
                         nodes
        """
        data = []
        segs = None
        sgn = 0.0
        if contour == 'a':
            segs = self.segA
            sgn = -1.0 # inwards pointing
        elif contour == 'b':
            segs = self.segB
            sgn = +1.0 # outwards pointing

        # compute and store each contribution on nodes
        nx, ny = {}, {}
        for ij in segs:
            i, j = ij
            xi, yi = self.grid.x(i), self.grid.y(i)
            xj, yj = self.grid.x(j), self.grid.y(j)
            dx, dy = xj - xi, yj - yi
            dRho = sqrt(dx**2 + dy**2)
            valX = 0.5 * dy/dRho
            valY = -0.5 * dx/dRho
            nx[i] = nx.get(i, 0.0) + valX
            nx[j] = nx.get(j, 0.0) + valX
            ny[i] = ny.get(i, 0.0) + valY
            ny[j] = ny.get(j, 0.0) + valY

        nxs, nys = [], []
        for ij in segs:
            i, j = ij
            nxs.append(nx[i])
            nys.append(ny[i])
            
        return nxs, nys       
        
    
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
                      default=0.001)
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

    ptsA = []
    ptsB = []
    print """
%s called with options %s
    """ % (sys.argv[0], str(sys.argv[1:]),)
    
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
        ntB = int( (b/a) * ntA )
        dtB = 2*pi/float(ntB)
        ptsB = [(R0 + b*cos(i*dtB + delta*sin(i*dtB)), kappa*b*sin(i*dtB)) \
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
        ptsB = gi.getContour2()
        
    dl = doubleGradShafranov()
    dl.setContourA(ptsA)
    dl.setContourB(ptsB)
    dl.generateGrid(a = options.area)
    
    xA, yA = dl.getXY('a')
    xB, yB = dl.getXY('b')
    # centered on segments
    nXA, nYA = dl.getNormalDerivativeOperator('a')
    nXB, nYB = dl.getNormalDerivativeOperator('b')
    ntA = len(xA)
    ntB = len(xB)

    gr = gLaplaceN.Green(nTor = 1)
    
    xSource, ySource = dl.midX, dl.midY
    print 'Source position %f, %f' % (xSource, ySource)
    
    def neumannDiracSource(xi, yi, xj, yj):
        xm = 0.5 * (xi + xj)
        ym = 0.5 * (yi + yj)
        gr.set(xm, ym, xSource, ySource)
        dx = xj - xi
        dy = yj - yi
        ds = sqrt(dx**2 + dy**2)
        val = (+ dy*gr.getDx1() - dx*gr.getDy1()) / ds
        return val * xSource # factor xSource due to chi -> psi transformation
    
    dl.setNeumann('a', neumannDiracSource)
    dl.setNeumann('b', neumannDiracSource)
    
    dl.solve(plot=options.plot)

    chiA = dl.getChi('a')
    chiB = dl.getChi('b')
    psiA = [xA[i]*chiA[i] for i in range(ntA)]
    psiB = [xB[i]*chiB[i] for i in range(ntB)]

    # exact values
    psiAExact = []
    for ij in dl.segA:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        gr.set(x, y, xSource, ySource)
        psiAExact.append( x * xSource * gr.get() )
    psiBExact = []
    for ij in dl.segB:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        gr.set(x, y, xSource, ySource)
        psiBExact.append( x * xSource * gr.get() )

    f = file('doubleGradShafranov.txt', 'w')
    print >> f, '# contour a: theta psi(Numeric) psi(Exact) error'
    for ij in dl.segA:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        th = atan2(y - ySource, x - xSource)
        gr.set(x, y, xSource, ySource)
        psiX = x * xSource * gr.get()
        print >> f, '%f %f %f %g' % (th, dl.psi[i], psiX, dl.psi[i]-psiX)
    print >> f, '# contour b: theta psi(Numeric) psi(Exact) error'
    for ij in dl.segB:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        th = atan2(y - ySource, x - xSource)
        gr.set(x, y, xSource, ySource)
        psiX = x * xSource * gr.get()
        print >> f, '%f %f %f %g' % (th, dl.psi[i], psiX, dl.psi[i]-psiX)
    f.close()  

    dt = 2*pi / float(ntA)
    dchiA = []
    for i in range(ntA):
        gr.set(xA[i], yA[i], xSource, ySource)
        dchiA.append( + nXA[i]*gr.getDx1() + nYA[i]*gr.getDy1() )

    dt = 2*pi / float(ntB)
    dchiB = []
    for i in range(ntB):
        gr.set(xB[i], yB[i], xSource, ySource)
        dchiB.append( + nXB[i]*gr.getDx1() + nYB[i]*gr.getDy1() )

    dPsiA = [nXA[i]*chiA[i] + xA[i]*dchiA[i] for i in range(ntA)]
    dPsiB = [nXB[i]*chiB[i] + xB[i]*dchiB[i] for i in range(ntB)]

    printStat('Response psi on (a): ', psiA)
    printStat('Exact psi on (a)   : ', psiAExact)
    print
    printStat('Response psi on (b): ', psiB)
    printStat('Exact psi on (b)   : ', psiBExact)
    print

    printStat('dpsi/dn on (a): ', dPsiA)
    printStat('dpsi/dn on (b): ', dPsiB)

if __name__ == '__main__': main()
