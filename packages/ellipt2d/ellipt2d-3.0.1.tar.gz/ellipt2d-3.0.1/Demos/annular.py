#!/usr/bin/env python

"""
Compute the Neumann response to applied Dirichlet boundary conditions
in an annular geometry
$Id: annular.py,v 1.3 2010/01/28 18:11:49 pletzer Exp $
"""

import Triangulate
import ellipt2d
import superlu
import sparse
import vector
import tkplot
from math import pi, sin, cos, sqrt

class Annular:

    def __init__(self, a=1.0, b=2.0, nt=16, area=0.1):
        """
        Ctor:
        a: small radius
        b: large radius
        """
        aNt = nt
        aDt = 2*pi/float(aNt)
        self.aPts = [(a*cos(i*aDt), a*sin(i*aDt)) for i in range(aNt)]
        bNt = int(aNt * b / a)
        bDt = 2*pi/float(bNt)
        self.bPts = [(b*cos(i*bDt), b*sin(i*bDt)) for i in range(bNt)]
        
        self.tri = Triangulate.Triangulate()
        self.tri.set_points(self.aPts + self.bPts)
        segs = [(i, i+1) for i in range(aNt-1)] + [(aNt-1,0)]
        segs += [(aNt+i, aNt+i+1) for i in range(bNt-1)] + [(aNt+bNt-1,aNt)]
        self.tri.set_segments(segs)
        self.tri.set_holes([(0., 0.)])
        self.area = area

    def getAContour(self):
        return self.aPts

    def getBContour(self):
        return self.bPts
        
    def setDirichlet(self, aPointVals, bPointVals):
        aNt = len(self.aPts)
        bNt = len(self.bPts)
        self.tri.set_attributes([(-1.0, aPointVals[i]) for i in range(aNt)] +
                                [(+1.0, bPointVals[i]) for i in range(bNt)])
        self.tri.triangulate(area=self.area)             
        self.nds = self.tri.get_nodes()
        #self.nds.plot()
        self.atts = self.tri.get_attributes()
        equ = ellipt2d.ellipt2d(self.nds, f_funct='1.0', g_funct='0.0', s_funct='0.0')
        self.aMat, self.rhs = equ.stiffnessMat()
        self.aMatModified = self.aMat.copy()
        self.rhsModified = self.rhs.copy()
        large = 1.23235435e8
        self.boundaryIndices = []
        for i in range(len(self.atts)):
            if abs(self.atts[i][0]) == 1.0:
                # on contour a or b
                self.aMatModified[i,i] = large
                self.rhsModified[i] = large * self.atts[i][1]
                self.boundaryIndices.append(i)
        print 'boundaryIndices = ', self.boundaryIndices
        self.boundaryIndices.sort()
        print 'boundaryIndices = ', self.boundaryIndices
        self.boundaryIndexMap = {}
        for i in range(len(self.boundaryIndices)):
            self.boundaryIndexMap[ self.boundaryIndices[i] ] = i
        self.boundaryEdges = []
        for e in self.tri.get_edges():
            if e[1] == 1:
                # boundary
                self.boundaryEdges.append( e[0] )

    def solveDirichletProblem(self):
        self.sol = superlu.solve(self.aMatModified, self.rhsModified)
        
    def computeNormalDerivative(self,):
        self.boundaryMat = sparse.sparse()
        for i, j in self.boundaryEdges:
            xi, yi = self.nds.x(i), self.nds.y(i)
            xj, yj = self.nds.x(j), self.nds.y(j)
            ds = sqrt( (xi-xj)**2 + (yi-yj)**2 )
##             refX, refY = 0.0, 0.0
##             dxi = xi - refX
##             dyi = yi - refY
##             dxj = xj - refX
##             dyj = yj - refY
##             sgn = (dxi * dyj - dxj * dyi) / abs(dxi * dyj - dxj * dyi)
##             # opposite sign if contour a
##             if self.atts[i] < 0.0: sgn *= -1.0
##             ds *= sgn
            diagTrm = ds / 3.0
            offDiag = ds / 6.0
            iBound = self.boundaryIndexMap[i]
            jBound = self.boundaryIndexMap[j]
            self.boundaryMat[iBound, iBound] = self.boundaryMat.get((i,i),0.) + diagTrm
            self.boundaryMat[jBound, jBound] = self.boundaryMat.get((j,j),0.) + diagTrm
            self.boundaryMat[iBound, jBound] = offDiag
            self.boundaryMat[jBound, iBound] = offDiag
        print 'boundaryIndexMap = ', self.boundaryIndexMap
        print 'boundMat = ', self.boundaryMat
            
        nBound = self.boundaryMat.size()[0]
        boundaryRhs = [0.0 for i in range(nBound)]
        for i in self.boundaryIndices:
            iBound = self.boundaryIndexMap[i]
            boundaryRhs[iBound] = - self.rhs[i]
            for j in self.nds.linkedNodes(i):
##                 print 'i, j=', i, j, ' x,y=',self.nds.x(i), self.nds.y(i), ' iBound=', iBound, \
##                       ' Aij=', self.aMat[i,j], ' xj=', self.sol[j], ' bi=', self.rhs[i]
                boundaryRhs[iBound] += self.aMat[i,j] * self.sol[j]

# check
        for i in self.boundaryIndices:
            iBound = self.boundaryIndexMap[i]
            aMatContrib = 0.0
            for j in self.nds.linkedNodes(i):
                aMatContrib += self.aMat[i,j] * self.sol[j]
            print 'i=%d iBound=%d A contribution=%f b contribution=%f' % (i, iBound, aMatContrib, self.rhs[i])

        # solve boundary system
        self.boundUPrime = superlu.solve(self.boundaryMat, boundaryRhs)
        print 'u-prime=', self.boundUPrime, len(self.boundUPrime)
        
    def check(self):
        internalEnergy = sparse.dotDot(self.sol, self.aMat, self.sol)
        sourceTerm = vector.dot(self.sol, self.rhs)
        boundSol = vector.vector([self.sol[i] for i in self.boundaryIndices])
        boundaryTerm = sparse.dotDot(boundSol, self.boundaryMat, self.boundUPrime)
        print 'internal energy = ', internalEnergy
        print 'boundaryTerm + sourceTerm = ', boundaryTerm, ' + ', sourceTerm, ' = ', \
               boundaryTerm + sourceTerm
        
    def getNormalDerivativeOnA(self):
        return []
    
    def getNormalDerivativeOnB(self):
        return []

    def plot(self, width=1200, height=900):
        import Tkinter
        root = Tkinter.Tk()
        frame = Tkinter.Frame(root)
        frame.pack()
        canvas = Tkinter.Canvas(bg="white", width=width, height=height)
        canvas.pack()
        tkplot.tkplot(canvas, self.nds, self.sol, 1, 1, 1, width, height)
        root.mainloop()
    
######################################################################

def main():
    a = 0.5
    b = 1.0
    nt = 16
    ann = Annular(a=a, b=b, nt=nt, area=0.1)
    aPts = ann.getAContour()
    bPts = ann.getBContour()
    aPointVals = [0.0 for i in range(len(aPts))]
    bPointVals = [1.0 for i in range(len(bPts))]
    ann.setDirichlet(aPointVals, bPointVals)
    ann.solveDirichletProblem()
    ann.computeNormalDerivative()
    ann.check()
    print ann.getNormalDerivativeOnA()
    print ann.getNormalDerivativeOnB()
    ann.plot()
    
if __name__ == '__main__': main()
