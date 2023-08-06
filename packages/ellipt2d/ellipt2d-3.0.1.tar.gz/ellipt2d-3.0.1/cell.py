#!/bin/env python
# $Id: cell.py,v 1.22 2013/12/20 22:38:27 pletzer Exp $
#

"""
ellipt2d: data structure to hold the (3) nodes of the triangular cells
"""
from types import *
from node import node
from triangle import triangle
import reg2tri
import colormap
import interp
from functools import reduce

def nodes2cells(node_object):

	res = {}

	index = 0
	all_nodes={}
	
	# find nodes that are recursively linked

	for ia in node_object.nodes():
		for ib in node_object.linkedNodes(ia):
			for ic in node_object.linkedNodes(ib):

				if ia==ic: continue
				
				if ia in node_object.linkedNodes(ic):
					nodes = [ia, ib, ic]
					nodes.sort()
					t = triangle(node_object, nodes[0], nodes[1], nodes[2])
					if t.area < 0. :
						na, nb = nodes[1], nodes[0]
						nodes[0], nodes[1] = na, nb
					tnodes = tuple(nodes)
					if tnodes not in all_nodes:
						res[index] = nodes
						all_nodes[tnodes] = None
						index = index + 1
	return res
						
def interp_slow(cell_object, fnodes, xi, yi):
	"""
	Return linear interpolation in cell. Return None if no cell
	encompassing the point can be found.
	"""

	if len(fnodes) != len(cell_object.node.data):
		raise RuntimeError('Bad length in cells.interp')


	for index in cell_object.data:
		ia, ib, ic = cell_object.data[index]
		xa, ya = cell_object.node.data[ia][0]
		xb, yb = cell_object.node.data[ib][0]
		xc, yc = cell_object.node.data[ic][0]
		two_area = (xb-xa)*(yc-ya) - (xc-xa)*(yb-ya)
		xsi = ( (yc-ya)*(xi-xa)-(xc-xa)*(yi-ya) )/two_area
		if 0.0 <= xsi <= 1.0: 
			eta = (-(yb-ya)*(xi-xa)+(xb-xa)*(yi-ya) )/two_area
			if 0.0 <= eta <= 1.0-xsi:
				# (xi, yi) are located in cell index
				# now interpolate
				fa, fb, fc = fnodes[ia], fnodes[ib], fnodes[ic]
				return (fa + xsi*(fb-fa) + eta*(fc-fa))
	return None



class cell:
	"""
	From node object and its connection table, build a cell data dictionary
	storage format: { index: (inodea, inodeb, inodec) }
	"""

	def __init__(self, node_object):

		self.node = node_object
		self.data = nodes2cells(node_object)


	def centre(self, index):
		"""
		get coordinate (xc, yc) of cell's centre of gravity 
		"""
		ia, ib, ic = self.data[index][0], self.data[index][1], self.data[index][2]
		xc = (self.node.x(ia) + self.node.x(ib) + self.node.x(ic))/3.
		yc = (self.node.y(ia) + self.node.y(ib) + self.node.y(ic))/3.
		return (xc, yc)

	def vector_dot_grad(self, v, index, nodeVector):
		"""
		Compute the gradient along given vector
		@param v 2-element vector
		@param index cell index
		@param nodeVector
		"""
		ia, ib, ic = self.data[index][0], self.data[index][1], self.data[index][2]
		xa, ya = self.node.data[ia][0]
		xb, yb = self.node.data[ib][0]
		xc, yc = self.node.data[ic][0]
		fa, fb, fc = nodeVector[ia], nodevector[ib], nodevector[ic]
		two_area = (xb-xa)*(yc-ya) - (xc-xa)*(yb-ya)

		dxsi_dx = + (yc - ya)/two_area
		dxsi_dy = - (xc - xa)/two_area
		deta_dx = - (yb - ya)/two_area
		deta_dy = + (xb - xa)/two_area
		
		return v[0]*dxsi_dx*(fb - fa) + v[1]*dxsi_dy*(fb - fa) + \
		       v[0]*deta_dx*(fc - fa) + v[1]*deta_dy*(fc - fa)

	def find_index(self, xi, yi, guess_indices=[]):
		def check_indices(ia, ib, ic): 
			xa, ya = self.node.data[ia][0]
			xb, yb = self.node.data[ib][0]
			xc, yc = self.node.data[ic][0]
			two_area = (xb-xa)*(yc-ya) - (xc-xa)*(yb-ya)
			xsi = ( (yc-ya)*(xi-xa)-(xc-xa)*(yi-ya) )/two_area
			if 0.0 <= xsi <= 1.0: 
				eta = (-(yb-ya)*(xi-xa)+(xb-xa)*(yi-ya) )/two_area
				if 0.0 <= eta <= 1.0-xsi:
					return True, xsi, eta
			return False, -1,-1
		for index in guess_indices:
			a, b, c = self.data[index]
			bSuccess, xsi, eta = check_indices(a, b, c)
			if bSuccess: return index, xsi, eta

		for index, (a,b,c) in list(self.data.items()):
			bSuccess, xsi, eta = check_indices(a, b, c)
			if bSuccess: return index, xsi, eta
		return None, None, None
		
	def interp_slow(self, fnodes, xi, yi, guess_indices=[]):
		"""
		Return linear interpolation in cell. Return None if no cell
		encompassing the point can be found.
		"""

		if len(fnodes) != len(self.node.data):
			raise RuntimeError('Bad length in cells.interp')

		index, xsi, eta=self.find_index(xi, yi, guess_indices)
		if index is not None:
			# (xi, yi) are located in cell index
			# now interpolate
			ia, ib, ic = self.data[index]
			fa, fb, fc = fnodes[ia], fnodes[ib], fnodes[ic]
			return (fa + xsi*(fb-fa) + eta*(fc-fa))
		else: return None

	def interp_slow_ex(self, fnodes, xi, yi, guess_indices=[]):
		"""
		Return linear interpolation in cell. Return None if no cell
		encompassing the point can be found.
		"""

		if len(fnodes) != len(self.node.data):
			raise RuntimeError('Bad length in cells.interp')

		index, xsi, eta=self.find_index(xi, yi, guess_indices)
		if index is not None:
			# (xi, yi) are located in cell index
			# now interpolate
			ia, ib, ic = self.data[index]
			fa, fb, fc = fnodes[ia], fnodes[ib], fnodes[ic]
			return (fa + xsi*(fb-fa) + eta*(fc-fa)), index, xsi, eta
		else: return None

	def interp_ex(self, fnodes, xi, yi, outside=None, guess_indices=[]):
		"""
		Return linear interpolation in cell. Return outside if no cell
		encompassing the point can be found.
		"""
		import interp
		return interp.interp_ex(self.data, self.node.data, fnodes, xi, yi, outside, guess_indices)

	def interp(self, fnodes, xi, yi, outside=None):
		"""
		Return linear interpolation in cell. Return outside if no cell
		encompassing the point can be found.
		"""
		return interp.interp(self.data, self.node.data, fnodes, xi, yi, outside)
	
	def interpUniform(self, fnodes, nx1, xmin, xmax, ny1, ymin, ymax, outside=None):
		"""
		Return interpolation of f on unstructed grid nodes to uniform grid positions
		given by xgrid, ygrid
		"""
		if len(fnodes) != len(self.node.data):
			raise RuntimeError('Bad length in cells.interpRegular')

		dx = (xmax-xmin)/float(nx1-1)
		dy = (ymax-ymin)/float(ny1-1)

		res = [[outside for i in range(nx1)] for j in range(ny1)]

		for index in self.data:
			ia, ib, ic = self.data[index]
			xa, ya = self.node.data[ia][0]
			xb, yb = self.node.data[ib][0]
			xc, yc = self.node.data[ic][0]
			xCellmin = min(xa, xb, xc)
			xCellmax = max(xa, xb, xc)
			yCellmin = min(ya, yb, yc)
			yCellmax = max(ya, yb, yc)
			i1x = max(    0, int((xCellmin-xmin)//dx))
			i2x = min(nx1-1, int((xCellmax-xmin)//dx))
			i1y = max(    0, int((yCellmin-ymin)//dy))
			i2y = min(ny1-1, int((yCellmax-ymin)//dy))
			for j in range(i1y, i2y+1):
				for i in range(i1x, i2x+1):
					xi, yi = xmin + i*dx, ymin + j*dy
					two_area = (xb-xa)*(yc-ya) - (xc-xa)*(yb-ya)
					xsi = ( (yc-ya)*(xi-xa)-(xc-xa)*(yi-ya) )/two_area
					if 0.0 <= xsi <= 1.0:
						eta = (-(yb-ya)*(xi-xa)+(xb-xa)*(yi-ya) )/two_area
						if 0.0 <= eta <= 1.0-xsi:
							# regular grid node inside cell
							fa, fb, fc = fnodes[ia], fnodes[ib], fnodes[ic]
							res[j][i] = (fa + xsi*(fb-fa) + eta*(fc-fa))
		return res
			
		

	def out(self):
		"""
		This method prints out the contents of the cell data
		structure dictionary.
		"""
		print('# index -- node array')
		for index in list(self.data.keys()):
			print((index, self.data[index]))

	def boxsize(self):
		large = 1000.0
		xmin= large
		xmax=-large
		ymin= large
		ymax=-large
		for inode in list(self.node.data.keys()):
			if self.node.data[inode][0][0] < xmin:
				xmin = self.node.data[inode][0][0]
			if self.node.data[inode][0][0] > xmax:
				xmax = self.node.data[inode][0][0]
			if self.node.data[inode][0][1] < ymin:
				ymin = self.node.data[inode][0][1]
			if self.node.data[inode][0][1] > ymax:
				ymax = self.node.data[inode][0][1]
		return (xmin, ymin, xmax, ymax)
		

  
    

if __name__ == "__main__":
	
	import interp
	
	# 1. construct grid
	
	xmin = 0.0
	xmax = 1.0
	ymin = 0.0
	ymax = 1.2
	nx1 = 11 #21
	ny1 = 5 #11
	mygrid = reg2tri.rect2criss((xmin, ymin, xmax, ymax), nx1, ny1)
	
	mycells = cell(mygrid)	    
	
	import vector
	f = [0.0 for i in range(len(mygrid))]
	for i in range(len(mygrid)):
		x, y = mygrid.x(i), mygrid.y(i)
		f[i] = x**2 + x*y**3
	sum1 = sum2 = 0.0
	for i in range(len(mygrid)):
		x, y = mygrid.x(i), mygrid.y(i)
		try:
			sum1 += mycells.interp_slow(f, x, y)
		except:
			print(('sum1: i, x, y = ', i, x, y))
		try:
			sum2 += mycells.interp(f, x, y)
		except:
			print(('sum2: i, x, y = ', i, x, y))
	print((sum1, sum2, reduce(lambda x,y:x+y, f, 0.0)))
	print((mycells.interp_slow(f, 0.5, 0.5)))
	print((mycells.interp_slow(f, 1.5, 0.5)))
	print((mycells.interp_slow(f, 0.5, 1.5)))
	print((mycells.interp_slow(f, xmin, ymin)))
	
	print(('-'*10))
	print((mycells.interp(f, 0.5, 0.5)))
	print((mycells.interp(f, 1.5, 0.5)))
	print((mycells.interp(f, 0.5, 1.5)))
	print((mycells.interp(f, xmin, ymin)))
	    










