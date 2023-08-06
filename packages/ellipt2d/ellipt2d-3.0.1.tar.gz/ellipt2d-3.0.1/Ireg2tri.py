#!/usr/bin/env python
# $Id: Ireg2tri.py,v 1.18 2013/12/20 22:58:30 pletzer Exp $
# convert various mesh geometries to triangular mesh
#

"""
ellipt2d: domain triangulation
"""

from node import node
import triang

MIN_AREA_CONSTRAINT = 1.e-10

class Ireg2tri:
    """
    Takes care of irregular mesh generation and refinement by interfacing
    with TRIANGLE (a triangulation code in C). One object should be created
    for each triangulation to be performed and the previous object should be 
    deleted before creation of the next object.
    """

    def __init__(self,area = 0.0):
	"""
	Initializes the intial area constraint to the value of the argument area
        and defaults the mode to 'p'(planar straight line graph triangulation).
	'p' triangulations require segmentlist. If in addition there are holes
        in the domain then holelist and regionlist are also required.
	"""
        self.area = area
        self.isReady = 0

        # basic TRIANGLE options
        # z: indexing starts at zero
        # e: edges
        # q: quality mesh (can add number such as 30.0 to specify min angle)
	self.mode = 'zeq27'

    def __del__(self):
	"""
	Frees up memory used by Triangle.
	"""
        triang.delete()

    def setUpConvexHull(self,
                        listofpoints,
                        seglist = [],
                        regionlist=[],
                        holelist=[],
                        nattr=4):
	"""
	Sends its arguments to Triangle for proper domain intialization.
	This is necessary for every triangulation. However, there are
        many variants depending on the domain in question. For instance
        if there are no concavities or holes then one only need to specify
        the list of points. Otherwise seglist must be specified. If in addition
        there are holes then holelist must also be specified.
	
	listofpoints = [(x1,y1),(x2,y2)...]
	seglist = [(node_number_a,node_number_b)...]
	holelist = [(x_hole_1,y_hole_1)...]
	regionlist (obsolete)
        nattr = number of attributes per node. This can be used for interpolating from one
        mesh to a finer mesh (see refine, setAttributes and get Attributes.

	"""
        if (len(seglist) != 0): self.mode = 'p'+self.mode

	triang.setUpConvexHull(listofpoints, seglist, holelist,regionlist, nattr)
        self.isReady = 1

    def setUpDirichlet(self,dB):
	"""
	Takes a Dirichlet boundary object and uses it to properly set
        boundary node attributes. Subsequently use updateDirichlet to correct
        the boundary conditions after invoking either the triangulate or
        refine methods.
	"""
        if not self.isReady:
            raise RuntimeError('Prior call to setUpConvexHull needed!')
        triang.setUpDirichlet(dB.getData())

    def updateDirichlet(self,dB):
	"""
	Updates a DirichletBound object data structure after triangulation.
	Changes reflect interpolation due to added (Steiner) boundary points.
        Typically, the user would create a DirichletBound object (associate
        boundary values to each boundary point), invoke setUpDirichlet, do
        the triangulation (or mesh refinement), and then call updateDirichlet.
	"""
        if not self.isReady:
            raise RuntimeError('Prior call to setUpConvexHull needed!')
        dB.setData(triang.updateDirichlet())
        
    def setAttributes(self,attribs):
	"""
	Sets node attributes. The number of attributes should be set
        in the setUpConvexHull method. This method can be used to
        interpolate between meshes. It can also be used to handle
        Robin or Neumann boundary conditions that require
        interpolation during triangulation.
        
        The number of attributes per node (nattr) is set in setUpConvexHull.

	attribs = [[attrib11,attrib12,...], [attrib21,attrib22,...],...]

        or

        attribs = [attrib1,attrib2,attrib3,attrib4...] if nattr = 1
	"""
        if not self.isReady:
            raise RuntimeError('Prior call to setUpConvexHull needed!')
        triang.setAttributes(attribs)

    def getAttributes(self):
	"""
	Returns the attribute dictionary from Triangle. Used after triangulation 
        to get updated attribute information. The new information can be used
        to update Boundary value objects.

        Returns a nested list

        [[attrib11,attrib12,...], [attrib21,attrib22,...],...]

        or [attrib1,attrib2,attrib3,attrib4...] if nattr = 1
	"""
        if not self.isReady:
            raise RuntimeError('Prior call to setUpConvexHull needed!')
        return triang.getAttributes()
    
    def triangulate(self):
	"""
	Triangulates the previously specified (by setUpConvexHull(...)) domain
	using the area constraint set during initialization and the eventual mode
        setting witch depends on which lists are specified for setUpConvexHull(...).
	"""
        if not self.isReady:
            raise RuntimeError('Prior call to setUpConvexHull needed!')
        grid = node()
        mode = self.mode + 'sli'
    
        if self.area > MIN_AREA_CONSTRAINT:
            mode += ('a%.15f' % self.area)

        print(('\narea = %.15f mode = %s \n' % (self.area, mode)))
        data = triang.triangulate(mode)
        grid.setData(data)
        return grid

        
    def refine(self,iter=1,area_ratio=2.0):
	"""
	Refines a previously generated mesh by halving the current area constraint.
        iter: number of refinement iterations
        area_ratio: area contraint is divided by area_ratio at each iteration
	A node object is returned.
	"""
        if not self.isReady:
            raise RuntimeError('Prior call to setUpConvexHull and triangulate needed!')
        for i in range(max(iter,1)-1):
            self.area /= area_ratio
            mode = 'r' + self.mode + 'cezs'
            if self.area > MIN_AREA_CONSTRAINT:
                mode += ('a%.15f'% self.area)
            d = triang.refine(mode)
        self.area /= area_ratio
        mode = 'r' + self.mode + 'cezs'
        if self.area > MIN_AREA_CONSTRAINT:
            mode += ('a%.15f'% self.area)
        data = triang.refine(mode)
        grid = node()
        grid.setData(data)
        return grid








