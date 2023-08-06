#!/usr/bin/env python

from ellipt2d import ellipt2d
from Ireg2tri import Ireg2tri
import vector
import time, os

class demo_Triangulation:
    """
    This demonstrates the use of the trinagulation routines..
    """
 
    def __init__(self):

        points = []
        seglist = []
        holelist = []
        regionlist = []

	points = [(0.0,0.0),(0.2,0.0),(0.6,0.0),(0.8,0.0),(1.0,0.0),(0.0,1.0)]
	seglist = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]


        initialAreaBound = 0.01
        meshgen = Ireg2tri(initialAreaBound)
        meshgen.mode = 'zeq32'
        meshgen.setUpConvexHull(points,seglist,regionlist,holelist)

        self.grid = meshgen.triangulate()
	self.grid = meshgen.refine(3)
        self.grid.plot()


if __name__ == "__main__":

    
    a = demo_Triangulation()
    
