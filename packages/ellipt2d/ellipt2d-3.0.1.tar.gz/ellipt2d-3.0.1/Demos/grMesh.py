VERSION = "$Id: grMesh.py,v 1.4 2009/11/18 15:43:52 pletzer Exp $"

"""
Compute the response matrices lambda = A * d lambda/dn for a domain delimited
by 2 arbitrary contours

"""

from Triangulate import Triangulate
from math import sqrt

class Mesh:

    def __init__(self):
        """
        Constructor
        """
        self.tri = Triangulate()

    def generate(self, points1, points2,
                 maxArea=None, minAngle=27.0):
        """
        Generate triangulation
        @param points1 list of [(x,y),...] points (assumed to be closed)
        @param points2 list of [(x,y),...] points (assumed to be closed)
        @param maxArea max triangle area
        @param minAngle min angle (< 33 deg)
        """
        
        n1 = len(points1)
        n2 = len(points2)
        self.segments1 = [ (i, i+1) for i in range(n1-1) ] \
                         + [ (n1-1, 0) ]
        self.segments2 = [ (i, i+1) for i in range(n1, n1+n2-1) ] \
                         + [ (n1+n2-1, n1) ]
        #
        # attributes used to locate segments on contours 1 and 2.
        #
        attrs = [(float(i),) for i in range(n1)] + \
                [(float(n1+i),) for i in range(n2)]
        
        # average for contour 1 is hole position
        x0 = reduce(lambda x,y:x+y, \
                    [points1[i][0] for i in range(n1)]) / float(n1)
        y0 = reduce(lambda x,y:x+y, \
                    [points1[i][1] for i in range(n1)]) / float(n1)
        holes = [ (x0, y0) ]

        self.tri.set_points( points1 + points2 )
        self.tri.set_attributes( attrs )
        self.tri.set_segments( self.segments1 + self.segments2 )
        self.tri.set_holes( holes )

        if maxArea == None:
            maxDs = max( [ sqrt( (points2[i+1][0]-points2[i][0])**2 +\
                                 (points2[i+1][1]-points2[i][1])**2 ) \
                           for i in range(n2-1) ] )
            maxArea = 0.5 * maxDs**2

        self.tri.triangulate(area=maxArea, mode='pzq%fe' % minAngle)
        self.grd = self.tri.get_nodes()
        self.edges = self.tri.get_edges()
        self.attributes = self.tri.get_attributes()

        self.nodes1 = [i for i in range(n1)]
        self.nodes2 = [i for i in range(n1, n1+n2)]

        self.points1 = points1
        self.points2 = points2

        self.boundarySegs1 = [ ]
        self.boundarySegs2 = []
        for e in self.edges:
            if e[1] == 1:
                i, j = e[0]
                if 0 <= i < n1 and 0 <= j < n1:
                    self.boundarySegs1.append(e[0])
                if n1 <= i < n1 + n2 and n1 <= j < n1 + n2:
                    self.boundarySegs2.append(e[0])

    def getContour1(self):
        """
        @return point coordinates on contour 1 (excluding Steiner points)
        """
        return self.points1
    

    def getContour2(self):
        """
        @return point coordinates on contour 2 (excluding Steiner points)
        """
        return self.points2
    
    def getGrid(self):
        """
        @return grid object for ellipt2d
        """
        return self.grd

    def getNodes1(self):
        """
        @return nodes on contour 1
        """
        return self.nodes1

    def getNodes2(self):
        """
        @return nodes on contour 2
        """
        return self.nodes2

    def getSegments1(self):
        """
        @return segments on contour 1 as a list of index tuples (excluding Steiner points)
        """
        return self.segments1
        
    def getSegments2(self):
        """
        @return segments on contour 2 as a list of index tuples (excluding Steiner points)
        """
        return self.segments2

    def getAllSegments1(self):
        """
        @return segments on contour 1 as a list of index tuples (including Steiner points)
        """
        return self.segments1
        
    def getAllSegments2(self):
        """
        @return segments on contour 2 as a list of index tuples (including Steiner points)
        """
        return self.segments2

    def getEdges(self):
        """
        @return edges 
        """
        return self.edges

        
    def getAttributes(self):
        """
        @return location attribute (used to determine whether a point is on a given
        contour or not)
        """
        return self.attributes

    def show(self):
        """
        Plot mesh
        """
        self.grd.plot()

######################################################################

def main():

    import grInput
    gri = grInput.Input()
    gri.open(filename = 'grin.dat')

    grm = Mesh()
    grm.generate(points1 = gri.getContour1(), points2 = gri.getContour2())
    grm.show()

if __name__ == '__main__': main()
