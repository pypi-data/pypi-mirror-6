#!/usr/bin/env python

"""
Solve ill-posed Neumann problem
  normal derivative is -1 at entrance, +1 at exit, and 0 elsewhere

  $Id: obstacle.py,v 1.3 2009/06/25 16:54:13 pletzer Exp $

"""

from Triangulate import Triangulate
from ellipt2d import ellipt2d
from NeumannBound import NeumannBound
import superlu
from math import sqrt

def generateMesh(boxL, boxH, obsL, obsH, obsPos,
                 maxArea, minAngle):
    #
    eps = sqrt(maxArea) * 0.5 # cutting corners
    points = [(eps,0.), (obsPos-eps, 0.), (obsPos, eps), (obsPos, obsH-eps),
              (obsPos+eps, obsH), (obsPos+obsL-eps, obsH),
              (obsPos+obsL, obsH-eps), (obsPos+obsL, eps), (obsPos+obsL+eps, 0.0), (boxL-eps, 0.), 
              (boxL, eps), (boxL, boxH-eps),
              (boxL-eps, boxH), (0.+eps, boxH),
              (0., boxH-eps), (0., eps)]
    
    segments = [(i,i+1) for i in range(len(points)-1)] + [(len(points)-1,0)]
    
    # attributes
    # the 1st attribute is the Neumann boundary value
    # the 2nd attribute tags segments that are on top of
    # obstacle (for computing lift)
    attrs = [(0.,0.), (0.,0.), (0.,0.), (0.,0.),
             (0.,1.), (0.,1.),
             (0.,0.), (0.,0.), (0.,0.), (0., 0.), 
             (1.,0.), (1.,0.),
             (0.,0.), (0.,0.),
             (-1.,0.), (-1.,0.),]

    tri = Triangulate()
    tri.set_points(points)
    tri.set_attributes(attrs)
    tri.set_segments(segments)
    tri.set_holes( [] )
    tri.triangulate(area=maxArea, mode='pzq%fe' % minAngle)
    return {'nodes': tri.get_nodes(), 'edges': tri.get_edges(),
            'attributes': tri.get_attributes()}

class ObstacleLaplace:

    def __init__(self, boxL=5.0, boxH=2.0, obsL=1.0, obsH=0.9*2.0, obsPos=2.0,
                 maxArea=0.001, minAngle=32.0):
        self.grd = generateMesh(boxL, boxH, obsL, obsH, obsPos,
                 maxArea, minAngle)
        #self.grd['nodes'].plot()
        self.equ = ellipt2d(self.grd['nodes'], '1.', None, None)
        self.Amat, self.rhs = self.equ.stiffnessMat()
        # Neumann BCs
        self.nb = NeumannBound()
        attrs = self.grd['attributes']
        for e in self.grd['edges']:
            if e[1] == 1:
                # boundary edge
                i, j = e[0]
                ai, aj = attrs[i][0], attrs[j][0]
                # segment is node average
                if ai and aj:
                    # only apply explicitely if non-zero
                    self.nb[e[0]] = 0.5 * (ai + aj)
        # change rhs vector
        self.equ.neumannB(self.nb, self.rhs)
        #
        # fix floating constant
        #
        self.Amat[0,0] = 1.e10; self.rhs[0] = 0.0
        
        self.sol = superlu.solve(self.Amat, self.rhs)
        uMin = min(self.sol)
        uMax = max(self.sol)
        print 'min, max, (max-min): %g %g %g' % (uMin, uMax, uMax-uMin)

    def computeLift(self):
        res = 0.0
        attrs = self.grd['attributes']
        grd = self.grd['nodes']
        for e in self.grd['edges']:
            if e[1] == 1:
                # boundary edge
                i, j = e[0]
                ai, aj = attrs[i][1], attrs[j][1]
                if ai + aj == 2:
                    xi, yi = grd.x(i), grd.y(i)
                    xj, yj = grd.x(j), grd.y(j)
                    dx = xj - xi
                    dy = yj - yi
                    ds = sqrt(dx**2 + dy**2)
                    # tangent velocity
                    uTan = (self.sol[j] - self.sol[i]) / ds
                    # rho = 1, V = 1
                    res += 0.5 * ds * (uTan**2 - 1.0)
                    #print i,j, 'xi, xj=', xi, xj, ds, self.sol[i], self.sol[j], 'uTan=', uTan, uTan*ds
        return res
                

    def plot(self, width=600, height=300):
        import Tkinter
        import tkplot
        
        root = Tkinter.Tk()
        canvas = Tkinter.Canvas(bg="white", width=width, height=height)
        canvas.pack()
        tkplot.tkplot(canvas, self.equ.grid, self.sol,
                      draw_mesh=0, node_no=0, add_minmax=1,
                      WIDTH=width, HEIGHT=height)
        tkplot.tkplot(canvas, self.equ.grid, self.nb,
                      draw_mesh=0, node_no=0,
                      WIDTH=width, HEIGHT=height)
        root.mainloop()
###################################################
def main():
    o1 = ObstacleLaplace()
    print 'lift: ', o1.computeLift()
    o1.plot()

if __name__ == '__main__': main()
