#!/usr/bin/env python

VERSION = "$Id: grResponseMatrix.py,v 1.10 2009/11/18 15:43:52 pletzer Exp $"

"""
Compute the response matrices lambda = A * d lambda/dn for a domain delimited
by 2 arbitrary contours

"""


from math import pi, cos, sin, sqrt, floor
from ellipt2d import ellipt2d
import vector
import dsupralu
import Tkinter
import tkplot
import re
import sys
import copy
import numpy

class ResponseMatrix:

    def __init__(self):
        """
        Constructor
        """
        pass

    def setTriangulation(self, tri):
        """
        set grid object
        @param grMesh instance
        """
        self.grd = tri.getGrid()
        self.edges = tri.getEdges()
        self.attributes = tri.getAttributes()
        self.nodes1 = tri.getNodes1()
        self.nodes2 = tri.getNodes2()
        self.points1 = tri.getContour1()
        self.points2 = tri.getContour2()
        self.n1 = len(self.points1)
        self.n2 = len(self.points2)
        
    def setOperators(self, f, g, s=None):
        """
        Set functions in -div f grad + g
        @param f function of x, y
        @param g function of x, y
        """

        self.f = f
        equ = ellipt2d(self.grd, f, g, s)
        aMatrix, self.rhs0 = equ.stiffnessMat()
        if g == None:
            print('INFO: solution is defined up to a constant')
            iNode = len(self.nodes1)
            print '      enforcing solution to be zero on node %d' % iNode
            aMatrix[iNode, iNode] = 1.23432534e8

        # LU decomposition
        m, n = aMatrix.size()
        self.handles = dsupralu.new(aMatrix, n)
        colperm = 2
        dsupralu.colperm(self.handles[0], colperm)
        dsupralu.lu(self.handles[0])

    def getRhs(self, normalDerivativeFunct):
        """
        Compute and return the rhs vector given an imposed normal derivative 
        @param normalDerivativeFunct externally supplied normal derivative function of the
               node indices
        @return the rhs vector
        """
        rhs = copy.copy(self.rhs0)
        print self.edges
        for s in self.edges:
            if s[1] == 0:
                # not a boundary edge
                continue
            i, j = s[0]
            xi, yi = self.grd.x(i), self.grd.y(i)
            xj, yj = self.grd.x(j), self.grd.y(j)
            ai = self.attributes[i][0]
            aj = self.attributes[j][0]
            ds = sqrt((xi - xj)**2 + (yi - yj)**2)
            # mid point
            x = 0.5*(xi + xj)
            y = 0.5*(yi + yj)
            amid = 0.5 * (ai + aj)
            # f at mid point
            fmid = eval(self.f)
            print fmid
            # amid is the average index
            normDeriv = normalDerivativeFunct(amid)
            contrib = 0.5 * fmid * normDeriv * ds
            rhs[i] += contrib
            rhs[j] += contrib
        return rhs

    def getResponse(self, nodes, rhs):
        """
        @param nodes list of node indices
        @param rhs right-hand side list returned by setUnitNormalDerivative
        @return solution for given rhs on nodes
        """

        self.solution = dsupralu.solve(self.handles[0], rhs)
        return [self.solution[i] for i in nodes]

###############################################################################

def main():

    import Tkinter
    import tkplot
    from grMesh import Mesh

    root = Tkinter.Tk()
    frame = Tkinter.Frame(root)
    frame.pack()
    w, h = 800, 800
    canvas = Tkinter.Canvas(bg="white", width=w, height=h)
    canvas.pack()

    rm = ResponseMatrix()
    a = 0.3
    b = 0.36
    r0 = 1.0
    elong = 1.7
    trian = 0.3
    nTor = 1
    # contour 1
    nt = 32
    dt = 2*pi/float(nt)
    pts1 = [ (r0+a*cos(i*dt + trian*sin(i*dt)), a*elong*sin(i*dt)) for i in range(nt) ]
    # contour 2
    nt = 32
    dt = 2*pi/float(nt)
    pts2 = [ (r0+b*cos(i*dt + trian*sin(i*dt)), b*elong*sin(i*dt)) for i in range(nt) ]

    tri = Mesh()
    tri.generate(pts1, pts2, maxArea=0.005, minAngle=32.0)
    #tri.show()
    rm.setTriangulation( tri )
        
    rm.setOperators(f='x', g='%d/x'%nTor**2)

    # response to d chi/dn = 1 on 1, and d chi/dn = 0 on 2
    
    def normDeriv(aIndex):
        if aIndex > rm.n1 - 1:
            # on contour 2
            return 0.0
        else:
            # on contour 1
            return -1.0

    rhs = rm.getRhs(normDeriv)
    print rhs

    solutionOn1 = rm.getResponse(rm.nodes1, rhs)
    solutionOn2 = rm.getResponse(rm.nodes2, rhs)

    print 'Response to norm deriv = 1 on 1, 0 on 2'
    print 'Response on 1 ', solutionOn1
    print 'Response on 2 ', solutionOn2

    tkplot.tkplot(canvas, rm.grd, rm.solution, 0, 1, 1,
                  title='response', WIDTH=w, HEIGHT=h)
    root.mainloop()

if __name__ == '__main__': main()
