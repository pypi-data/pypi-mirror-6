#!/usr/bin/env python
#
# convert various mesh geometries to triangular mesh
#

from node import node

"""
Given a n1*n2 array of regular (x, y) positions, the following methods return
a node object suitable for ellipt2d.
"""

def criss(xy):
	"""
	Rectangular to criss mesh generator

	Input:

	xy: a n1*n2 array of regular (x, y) positions
	[[(x1, y1), (x2, y2),...], ....]

	Output:

	A node object consisting of node #, (x,y) positions,
	and the NE-SW connections.

	
	"""
	grid = node({})
	nx1 = len(xy)
	ny1 = len(xy[0])
	inode = 0
	# fill-up positions
	for iy in range(ny1):
		for ix in range(nx1):
			x, y = xy[ix][iy][0], xy[ix][iy][1]
			grid.set(inode, (x, y))
			inode = inode + 1

	# fill-up connections
	for iy in range(ny1):
		for ix in range(nx1):
			ia = iy*nx1 + ix
			if ix < nx1-1:
				# east
				ib = ia + 1
				grid.connect(ia, ib)
			if ix < nx1-1 and iy < ny1-1:
				# north east
				ib = ia + nx1 + 1
				grid.connect(ia, ib)
			if iy < ny1-1:
				# north
				ib = ia + nx1
				grid.connect(ia, ib)
			if ix > 0:
				# west
				ib = ia - 1
				grid.connect(ia, ib)
			if ix > 0 and iy > 0:
				# south west
				ib = ia - nx1 - 1
				grid.connect(ia, ib)
			if iy > 0:
				# south
				ib = ia - nx1
				grid.connect(ia, ib)
	return grid
			
				
def cross(xy):
	"""
	Rectangular to cross mesh generator

	Input:

	xy: a n1*n2 array of regular (x, y) positions
	[[(x1, y1), (x2, y2),...], ....]

	Output:

	A node object consisting of node #, (x,y) positions,
	and the NW-SE connections

	"""
	grid = node({})
	nx1 = len(xy)
	ny1 = len(xy[0])
	inode = 0
	# fill-up positions
	for iy in range(ny1):
		for ix in range(nx1):
			x, y = xy[ix][iy][0], xy[ix][iy][1]
			grid.set(inode, (x, y))
			inode = inode + 1
			
	# fill-up connections
	for iy in range(ny1):
		for ix in range(nx1):
			ia = iy*nx1 + ix
			if ix < nx1-1:
				# east
				ib = ia + 1
				grid.connect(ia, ib)
			if iy < ny1-1:
				# north
				ib = ia + nx1
				grid.connect(ia, ib)
			if ix > 0 and iy < ny1-1:
				# north west
				ib = ia + nx1 - 1
				grid.connect(ia, ib)
			if ix > 0:
				# west
				ib = ia - 1
				grid.connect(ia, ib)
			if iy > 0:
				# south
				ib = ia - nx1
				grid.connect(ia, ib)
			if iy > 0 and ix < nx1-1:
				# south east
				ib = ia - nx1 + 1
				grid.connect(ia, ib)
	return grid

def crisscross(xy):
	"""
	Rectangular to criss-cross mesh generator

	Input:

	xy: a n1*n2 array of regular (x, y) positions
	[[(x1, y1), (x2, y2),...], ....]

	Output:

	A node object consisting of node #, (x,y) positions,
	and their connections

	"""
	grid = node({})
	ny1 = len(xy)
	nx1 = len(xy[0])
	inode = 0
	# fill-up positions
	for iy in range(ny1):
		# node points
		for ix in range(nx1):
			x, y = xy[iy][ix][0], xy[iy][ix][1]
			grid.set(inode, (x, y))
			inode = inode + 1
		if iy < ny1-1:
			# middle points
			for ix in range(nx1-1):
				x0, y0 = xy[iy][ix][0], xy[iy][ix][1]
				x1, y1 = xy[iy][ix+1][0], xy[iy+1][ix][1]
				x, y = x0 + (x1-x0)/2., y0 + (y1-y0)/2.
				grid.set(inode, (x,y))
				inode = inode + 1
			
			
	# fill-up connections
	for iy in range(ny1):
		for ix in range(nx1):
			ia = iy*(2*nx1-1) + ix
			if ix < nx1-1:
				# east
				ib = ia + 1
				grid.connect(ia, ib)
			if ix < nx1-1 and iy < ny1-1:
				# north east
				ib = ia + nx1
				grid.connect(ia, ib)
			if iy < ny1-1:
				# north
				ib = ia + 2*nx1 - 1
				grid.connect(ia, ib)
			if ix > 0 and iy < ny1-1:
				# north west
				ib = ia + nx1 - 1
				grid.connect(ia, ib)
			if ix > 0:
				# west
				ib = ia - 1
				grid.connect(ia, ib)
			if ix > 0 and iy > 0:
				# south west
				ib = ia - nx1
				grid.connect(ia, ib)
			if iy > 0:
				# south
				ib = ia - 2*nx1 + 1
				grid.connect(ia, ib)
			if iy > 0 and ix < nx1-1:
				# south east
				ib = ia - nx1 + 1
				grid.connect(ia, ib)
		if iy==ny1-1: break
		for ix in range(nx1-1):
			ia = iy*(2*nx1-1) + ix + nx1
			# ne
			ib = ia + nx1
			grid.connect(ia, ib)
			# nw
			ib = ia + nx1 - 1
			grid.connect(ia,ib)
			# sw
			ib = ia - nx1
			grid.connect(ia, ib)
       			# se
			ib = ia - nx1 + 1
			grid.connect(ia, ib)
			
	return grid

def rect2crisscross(xybox, nx1, ny1):
	"""
	Rectangular to crisscross mesh generator
	Returns a node object with NE-SW connections.

	xybox: a tuple containing xmin, ymin, xmax, ymax

	"""
	grid = node({})
	
	xmin, ymin, xmax, ymax = xybox
	dx, dy = xmax-xmin, ymax-ymin

	inode = 0
	# fill-up positions
	for iy in range(ny1):
		# node points
		for ix in range(nx1):
			x = xmin + dx*ix/float(nx1-1)  
			y = ymin + dy*iy/float(ny1-1)
			grid.set(inode, (x, y))
			inode = inode + 1
		if iy < ny1-1:
			# middle points
			for ix in range(nx1-1):
				x0 = xmin + dx*ix/float(nx1-1)  
				y0 = ymin + dy*iy/float(ny1-1)
				x1 = xmin + dx*(ix+1)/float(nx1-1)  
				y1 = ymin + dy*(iy+1)/float(ny1-1)
				x, y = x0 + (x1-x0)/2., y0 + (y1-y0)/2.
				grid.set(inode, (x,y))
				inode = inode + 1
			
			
	# fill-up connections
	for iy in range(ny1):
		for ix in range(nx1):
			ia = iy*(2*nx1-1) + ix
			if ix < nx1-1:
				# east
				ib = ia + 1
				grid.connect(ia, ib)
			if ix < nx1-1 and iy < ny1-1:
				# north east
				ib = ia + nx1
				grid.connect(ia, ib)
			if iy < ny1-1:
				# north
				ib = ia + 2*nx1 - 1
				grid.connect(ia, ib)
			if ix > 0 and iy < ny1-1:
				# north west
				ib = ia + nx1 - 1
				grid.connect(ia, ib)
			if ix > 0:
				# west
				ib = ia - 1
				grid.connect(ia, ib)
			if ix > 0 and iy > 0:
				# south west
				ib = ia - nx1
				grid.connect(ia, ib)
			if iy > 0:
				# south
				ib = ia - 2*nx1 + 1
				grid.connect(ia, ib)
			if iy > 0 and ix < nx1-1:
				# south east
				ib = ia - nx1 + 1
				grid.connect(ia, ib)
		if iy==ny1-1: break
		for ix in range(nx1-1):
			ia = iy*(2*nx1-1) + ix + nx1
			# ne
			ib = ia + nx1
			grid.connect(ia, ib)
			# nw
			ib = ia + nx1 - 1
			grid.connect(ia,ib)
			# sw
			ib = ia - nx1
			grid.connect(ia, ib)
       			# se
			ib = ia - nx1 + 1
			grid.connect(ia, ib)
			
	return grid

			

def rect2criss(xybox, nx1, ny1):
	"""
	Rectangular to regular to triangular mesh generator
	Returns a node object with NE-SW connections.

	xybox: a tuple containing xmin, ymin, xmax, ymax

	"""
	grid = node({})
	
	xmin, ymin, xmax, ymax = xybox
	for ix in range(0, nx1):
		for iy in range(0, ny1):
			inode = iy*nx1 + ix
			xval = xmin + (xmax-xmin)*ix/(nx1-1)
			yval = ymin + (ymax-ymin)*iy/(ny1-1)
			grid.set(inode, (xval, yval))
	
	for ix in range(0, nx1):
		for iy in range(0, ny1):
			ia = iy*nx1 + ix
			if ix < nx1-1:
				ib = ia + 1 # E connection
				grid.connect(ia, ib)
			if ix > 0:
				ib = ia - 1 # W connection
				grid.connect(ia, ib)
			if iy < ny1-1:
				ib = ia + nx1 # N connection
				grid.connect(ia, ib)
				if ix < nx1-1:
					ib = ib + 1 # NE connection
					grid.connect(ia, ib)
			if iy > 0:
				ib = ia - nx1 # S connection
				grid.connect(ia, ib)
				if ix > 0:
					ib = ib - 1 # SW connection
					grid.connect(ia, ib)
	return grid

def rect2cross(xybox, nx1, ny1):
	"""
	Rectangular to regular to triangular mesh generator
	Returns a node object with NW-SE connections.

	xybox: a tuple containing xmin, ymin, xmax, ymax

	"""
	grid = node({})
	
	xmin, ymin, xmax, ymax = xybox
	for ix in range(0, nx1):
		for iy in range(0, ny1):
			inode = iy*nx1 + ix
			xval = xmin + (xmax-xmin)*ix/(nx1-1)
			yval = ymin + (ymax-ymin)*iy/(ny1-1)
			grid.set(inode, (xval, yval))
	
	for ix in range(nx1):
		for iy in range(ny1):
			ia = iy*nx1 + ix
			if ix < nx1-1:
				ib = ia + 1 # E connection
				grid.connect(ia, ib)
			if ix > 0:
				ib = ia - 1 # W connection
				grid.connect(ia, ib)
			if iy < ny1-1:
				ib = ia + nx1 # N connection
				grid.connect(ia, ib)
				if ix > 0:
					ib = ib - 1 # NW connection
					grid.connect(ia, ib)
			if iy > 0:
				ib = ia - nx1 # S connection
				grid.connect(ia, ib)
				if ix < nx1-1:
					ib = ib + 1 # SE connection
					grid.connect(ia, ib)
	return grid


	


	
if __name__ == "__main__":

	pos = []
	nx1 = 2
	ny1 = 3

	grid = rect2crisscross((0.,0.,2.,1.), nx1, ny1)
	grid.out()
	
	for iy in range(ny1):
		pos.append([])
		for ix in range(nx1):
			#rho, phi = 1.+iy/float(ny1-1), pi*ix/float(nx1-1)
			#x, y = rho*cos(phi), rho*sin(phi)
			x, y = ix/float(nx1-1), iy/float(ny1-1)
			pos[iy].append((x, y))

	print('Criss-cross')
	grid = crisscross(pos)
	grid.out()
	
	print('Criss:')
	grid = criss(pos)
	grid.out()

	print('Cross:')
	grid = criss(pos)
	grid.out()







