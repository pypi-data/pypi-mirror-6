#!/usr/bin/env python

VERSION = "$Id: doubleLaplaceN.py,v 1.17 2010/03/11 21:12:36 pletzer Exp $"

"""
check validity of doubleLaplaceN
"""

from math import pi, cos, sin, sqrt
from Triangulate import Triangulate
from ellipt2d import ellipt2d
import superlu
import Tkinter
import tkplot

class doubleLaplaceN:

    def __init__(self, nTor=1,):
        self.nTor = nTor

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
        g = '%d/x' % self.nTor**2
        s = None
        self.equ = ellipt2d(self.grid, f, g, s)
        self.A, self.rhs = self.equ.stiffnessMat()

    def setNeumann(self, contour, funct):
        """
        Set Neumann boundary condition
        @param contour 'a' or 'b'
        @param funct function of (x, y)
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

        if plot:
            import utils
            utils.toVTK('doubleLaplaceN.vtk',
                        cells = self.equ.cells, grid = self.grid,
                        names = ['lambda'], fields = [self.chi])

            WIDTH = 600
            HEIGHT = 600
            root = Tkinter.Tk()
            frame = Tkinter.Frame(root)
            frame.pack()
            canvas = Tkinter.Canvas(bg="White",width=WIDTH,height=HEIGHT)
            canvas.pack()
            tkplot.tkplot(canvas,self.grid, self.chi, 0,0,1,WIDTH,HEIGHT)
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
    parser.add_option('-n', '--nTor', action='store', type="int",
                      dest="nTor", help="Toroidal mode number (!= 0)",
                      default=1)
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
        ntA = len(ptsA)
        ntB = len(ptsB)
    
    dl = doubleLaplaceN(nTor=options.nTor)

    dl.setContourA(ptsA)
    dl.setContourB(ptsB)
    
    dl.generateGrid(a=0.001)

    gr = gLaplaceN.Green(options.nTor)

    xSource, ySource = dl.midX, dl.midY
    print 'Source position %f, %f' % (xSource, ySource)
    
    def neumannDiracSource(xi, yi, xj, yj):
        xm = 0.5 * (xi + xj)
        ym = 0.5 * (yi + yj)        
        gr.set(xm, ym, xSource, ySource)
        
        dx = xj - xi
        dy = yj - yi
        ds = sqrt(dx**2 + dy**2)
        xDthNorm = dx / ds
        yDthNorm = dy / ds

        return yDthNorm*gr.getDx1() - xDthNorm*gr.getDy1()
        
    # normal pointing inwards
    dl.setNeumann('a', neumannDiracSource)
    dl.setNeumann('b', neumannDiracSource)
    
    dl.solve(plot=options.plot)

    chiA = dl.getChi('a')
    chiB = dl.getChi('b')

    # exact values
    chiAExact = []
    for ij in dl.segA:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        gr.set(x, y, xSource, ySource)
        chiAExact.append( gr.get() )
    chiBExact = []
    for ij in dl.segB:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        gr.set(x, y, xSource, ySource)
        chiBExact.append( gr.get() )

    print
    printStat('Response chi on (a): ', chiA)
    printStat('Exact    chi on (a): ', chiAExact)
    print
    
    printStat('Response chi on (b): ', chiB)
    printStat('Exact    chi on (b): ', chiBExact)
    print

    # to compare against Grin
    dchiA = []
    for i in range(ntA):
        xi, yi = ptsA[i]
        j = (i + 1) % ntA
        xj, yj = ptsA[j]
        xm = 0.5 * (xi + xj)
        ym = 0.5 * (yi + yj)
     
        dx = xj - xi
        dy = yj - yi
        ds = sqrt(dx**2 + dy**2)
        xDthNorm = dx / ds
        yDthNorm = dy / ds
        gr.set(xm, ym, xSource, ySource)

        dchiA.append( - yDthNorm*gr.getDx1() + xDthNorm*gr.getDy1() )

    dchiB = []
    for i in range(ntB):
        xi, yi = ptsB[i]
        j = (i + 1) % ntB
        xj, yj = ptsB[j]
        xm = 0.5 * (xi + xj)
        ym = 0.5 * (yi + yj)
     
        dx = xj - xi
        dy = yj - yi
        ds = sqrt(dx**2 + dy**2)
        xDthNorm = dx / ds
        yDthNorm = dy / ds
        gr.set(xm, ym, xSource, ySource)

        dchiB.append( yDthNorm*gr.getDx1() - xDthNorm*gr.getDy1() )
    
    
    printStat('Applied dchi on (a): ', dchiA)
    printStat('Applied dchi on (b): ', dchiB)

    f = file('doubleLaplaceN.txt', 'w')
    print >> f, '# contour a: theta chi(Numeric) chi(Exact) error'
    index = 0
    for ij in dl.segA:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        th = atan2(y - ySource, x - xSource)
        print >> f, '%f %f %f %g' % (th, chiA[index], chiAExact[index], \
                                     chiA[index] - chiAExact[index])
        index += 1
    print >> f, '# contour b: theta chi(Numeric) chi(Exact) error'
    index = 0
    for ij in dl.segB:
        i, j = ij
        x, y = dl.grid.x(i), dl.grid.y(i)
        th = atan2(y - ySource, x - xSource)
        print >> f, '%f %f %f %g' % (th, chiB[index], chiBExact[index], \
                                     chiB[index] - chiBExact[index])
        index += 1
    f.close()  
    

if __name__ == '__main__': main()
