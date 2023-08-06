#!/usr/bin/env python

"""
Compute the n = 0 d psi/d n responses to a given Dirichlet
boundary condition
$Id: grNZeroResponse.py,v 1.1 2009/11/03 13:13:52 pletzer Exp $
"""
import grMesh
import ellipt2d
import dsupralu

import math

class NZeroResponse:

    def __init__(self):
        pass

    def setContours(self, cont1, cont2, minAngle=27.0, maxArea=None):
        self.gm = grMesh.Mesh()
        self.gm.generate(points1 = cont1, points2 = cont2,
                         minAngle=minAngle, maxArea=maxArea)

    def assemble(self):
        # may need to allow for a source term...
        ffun, gfun, sfun = '1.0/x', '0', '0'
        self.equ = ellipt2d.ellipt2d(self.gm.getGrid(), ffun, gfun, sfun)
        self.aMat, self.rhs = self.equ.stiffnessMat()

    def setDirichletOnContour1(self, values):

        large = 1.312473287e8
        ndIndices = self.gm.getNodes1()
        n = len(ndIndices)
        for i in range(n):
            index = ndIndices[i]
            self.aMat[index, index] = large
            self.rhs[index] = large * values[i]          

    def setDirichletOnContour2(self, values):
        
        large = 1.312473287e8
        ndIndices = self.gm.getNodes2()
        n = len(ndIndices)
        for i in range(n):
            index = ndIndices[i]
            self.aMat[index, index] = large
            self.rhs[index] = large * values[i]

    def solve(self):
        m, n = self.aMat.size()
        handles = dsupralu.new(self.aMat, n)
        colperm = 2
        dsupralu.colperm(handles[0], colperm)
        dsupralu.lu(handles[0])
        self.solution = dsupralu.solve(handles[0], self.rhs)

    def getNormalDerivativeOnContour1(self):

        segs = self.gm.getSegments1()

        grd = self.gm.getGrid()
        n = len(segs)
        normalDerivative = [0.0 for i in range(n)]
        count = 0
        for seg in segs:
            i, j = seg
            xi, yi = grd.x(i), grd.y(i)
            xj, yj = grd.x(j), grd.y(j)
            dx, dy = xj - xi, yj - yi
            norm = math.sqrt( dx**2 + dy**2 )
            normalVect = [-dy/norm, dx/norm]
            neighi = grd.linkedNodes(i)
            neighj = grd.linkedNodes(j)
            for k in neighi:
                if k in neighj and k != j:
                    break
            xk, yk = grd.x(k), grd.y(k)
            fi, fj, fk = self.solution[i], self.solution[j], self.solution[k]
            two_area = (xj-xi)*(yk-yi) - (xk-xi)*(yj-yi)

            dxsi_dx = + (yk - yi)/two_area
            dxsi_dy = - (xk - xi)/two_area
            deta_dx = - (yj - yi)/two_area
            deta_dy = + (xj - xi)/two_area

            normalDerivative[count] = \
                                    normalVect[0]*(dxsi_dx*(fj - fi) + deta_dx*(fk - fi)) + \
                                    normalVect[1]*(dxsi_dy*(fj - fi) + deta_dy*(fk - fi))
            count += 1

        return normalDerivative
            
    def showSolution(self, width=800, height=1000):
        import Tkinter
        import tkplot
        root = Tkinter.Tk()
        canvas = Tkinter.Canvas(bg="white", width=width, height=height)
        canvas.pack()
        tkplot.tkplot(canvas, self.gm.getGrid(), f=self.solution,
                      draw_mesh=0, node_no=0,
                  add_minmax=1, WIDTH=width, HEIGHT=height)
        root.mainloop()

    def plotNormalDerivativeOnContour(self, width=400, height=600):
        pass

######################################################################

def testIter():

    import grInput

    gri = grInput.Input()
    gri.open(filename = 'grin.dat')

    g0 = NZeroResponse()
    cont1 = gri.getContour1()
    cont2 = gri.getContour2()
    g0.setContours(cont1, cont2)
    g0.assemble()

    n1 = len(cont1)
    n2 = len(cont2)
    dirichlet1 = [0.0 for i in range(n1)]
    xCntr, yCntr = 0.0, 0.0

    # compute plasma center
    for i in range(n1):
        xCntr += cont1[i][0]
        yCntr += cont2[i][1]
    xCntr /= float(n1)
    yCntr /= float(n1)

    for i in range(n1):
        x, y = cont1[i]
        # cylindrical angle
        theta = math.atan2(y - yCntr, x - xCntr)
        dirichlet1[i] = math.cos(theta)
        
    dirichlet2 = [0.0 for i in range(n2)]
    
    g0.setDirichletOnContour1(dirichlet1)
    g0.setDirichletOnContour2(dirichlet2)

    g0.solve()

    print g0.getNormalDerivativeOnContour1()
    
    g0.showSolution()

def testCircular():

    import sys
    print " Test program ", sys.argv[0];
    print " Usage: ", sys.argv[0],
    print " [# points boundary a] [# points boundary b] [R0] [a] [b] [kappa] [delta]"

    n1 = 64 # 20
    if len(sys.argv) > 1: n1 = int(sys.argv[1])
    
    n2 = n1
    if len(sys.argv) > 2: n2 = int(sys.argv[2])
    
    r0 = 20.0 # 1.0
    if len(sys.argv) > 3: r0 = float(sys.argv[3])
    
    a = 1.0 # 0.3
    if len(sys.argv) > 4: a = float(sys.argv[4])
    
    b = 2.0 # 1.2*a
    if len(sys.argv) > 5: b = float(sys.argv[5])

    kappa = 1.0 # 1.7
    if len(sys.argv) > 6: kappa = float(sys.argv[6])

    delta = 0.0 # 0.3
    if len(sys.argv) > 7: delta = float(sys.argv[7])

    dt = 2*math.pi / float(n1) 
    cont1 = [ (r0 + a*math.cos(i*dt + delta*math.sin(i*dt)), a*kappa*math.sin(i*dt)) \
              for i in range(n1) ]
    dt = 2*math.pi / float(n2)
    cont2 = [ (r0 + b*math.cos(i*dt + delta*math.sin(i*dt)), b*kappa*math.sin(i*dt)) \
              for i in range(n2) ]
    
    g0 = NZeroResponse()
    g0.setContours(cont1, cont2, minAngle=32.0, maxArea=0.001)
    g0.assemble()

    n1 = len(cont1)
    n2 = len(cont2)
    dirichlet1 = [0.0 for i in range(n1)]
    xCntr, yCntr = 0.0, 0.0

    # compute plasma center
    for i in range(n1):
        xCntr += cont1[i][0]
        yCntr += cont2[i][1]
    xCntr /= float(n1)
    yCntr /= float(n1)

    for i in range(n1):
        x, y = cont1[i]
        # cylindrical angle
        theta = math.atan2(y - yCntr, x - xCntr)
        dirichlet1[i] = 1.0 # math.cos(theta)
        
    dirichlet2 = [0.0 for i in range(n2)]
    
    g0.setDirichletOnContour1(dirichlet1)
    g0.setDirichletOnContour2(dirichlet2)

    g0.solve()

    dpsi_a_dn =  g0.getNormalDerivativeOnContour1()
    # compute average
    avg = 0.0
    minVal = + float('inf')
    maxVal = - float('inf')
    for e in dpsi_a_dn:
        avg += e
        minVal = min(minVal, e)
        maxVal = max(maxVal, e)
    avg /= float(len(dpsi_a_dn))
    print 'Average d psi(a)/dn = %f Min: %f Max: %f' % (avg, minVal, maxVal)
    
    g0.showSolution()

    
if __name__ == '__main__': testCircular()
