#!/usr/bin/env python
# $Id: cellipt2d.py,v 1.10 2013/12/20 04:44:52 pletzer Exp $
"""
ellipt2d: complex version with f a scalar
"""

import math
from csparse import csparse
from types import StringType
import cvector, time, cell
import triangle
import math
# need this in eval when passing string functions 
from math import *

onethird = 1.0/3.0
onesixth = 1.0/6.0
onetwelfth = 1.0/12.0
onefourth = 1.0/4.0


class ellipt2d:
    """
    General 2d elliptic solver (complex)
    """
    def __init__(self, grid, f_funct, g_funct, s_funct):
        """
	Elliptic solver constructor for equation 
	-div f_funct . grad v + g_funct v = s_funct:

	grid: node object of the form:
	{node: [(x,y), [connections], [boundary attributes]} 

        *NOTE* if f is a tensor use cellipt2dF class!

	f_funct: a (complex) scalar function, either a string function of 'x' and 'y'
        or a node vector or None (same as '0j' but faster).

	g_funct: a (complex) scalar string function of 'x' and 'y' or a vector of node
	values or None (same as '0j' but faster).

	s_funct:  a (complex) scalar string function of 'x' and 'y' or a vector of node
	values or None (same as '0j' but faster).
        """
	
	# make cells
	
        self.grid = grid
        [self.xmin, self.ymin, self.xmax, self.ymax] = self.grid.boxsize()
        self.cells = cell.cell(self.grid)

        #
        # f-function
        #
        if f_funct:
            if type(f_funct)==StringType:
                fNodes = [0.0 for i in range(len(grid))]
                for i in range(len(grid)):
                    x, y = grid.x(i), grid.y(i)
                    fNodes[i] = eval(f_funct, globals(),{'x':x, 'y':y}) 
            else:
                fNodes = f_funct

            # make f a cell vector
            self.fCells = [0.0 for k in self.cells.data]
            for k in self.cells.data:
                [ia, ib, ic] = self.cells.data[k]
                self.fCells[k] = (fNodes[ia] + fNodes[ib] + fNodes[ic])/3.0
        else:
            self.fCells = [0.0 for k in self.cells.data]

        #
        # g-function
        #
        if g_funct:
            if type(g_funct)==StringType:
                self.gNodes = [0.0 for i in range(len(grid))]
                for i in range(len(grid)):
                    x, y = grid.x(i), grid.y(i)
                    self.gNodes[i] = eval(g_funct, globals(),{'x':x, 'y':y}) 
            else:
               self.gNodes = g_funct
        else:
            self.gNodes = [0.0 for i in range(len(grid))]
           
        #
        # source function
        #
        if s_funct:
            if type(s_funct)==StringType:
                self.sNodes = [0.0 for i in range(len(grid))]
                for i in range(len(grid)):
                    x, y = grid.x(i), grid.y(i)
                    self.sNodes[i] = eval(s_funct, globals(),{'x':x, 'y':y}) 
            else:
               self.sNodes = s_funct
        else:
            self.sNodes = [0.0 for i in range(len(grid))]
                

    def stiffnessMat(self):
        """
	Assemble stiffness matrix
	"""
        amat = csparse({})
        source = cvector.zeros(len(self.grid.nodes()))
        for it in self.cells.data:
            i0 = self.cells.data[it][0]
            i1 = self.cells.data[it][1]
            i2 = self.cells.data[it][2]
            t0 = triangle.triangle(self.grid, i0, i1, i2)
            if t0.area < 0:
                i1, i2 = i2, i1
                t0 = triangle(self.grid, i0, i1, i2) 
            t1 = triangle.triangle(self.grid, i1, i2, i0)
            t2 = triangle.triangle(self.grid, i2, i0, i1)
            t = [t0, t1, t2]
            # take averages of f's
            fxx = fyy = self.fCells[it]
            # integral contributions
            # 0 => i0
            # 1 => i1
            # 2 => i2
            # contributions from f function. Only average f is required
            integ = [[0,0,0],[0,0,0],[0,0,0]]
            s = [0, 0, 0]
            for index1 in [0, 1, 2]:
                ga = self.gNodes[t[index1].ia]
                gb = self.gNodes[t[index1].ib]
                gc = self.gNodes[t[index1].ic]
                gabc = [ga, gb, gc] 
                sa = self.sNodes[t[index1].ia]
                sb = self.sNodes[t[index1].ib]
                sc = self.sNodes[t[index1].ic]
                sabc = [sa, sb, sc] 
                s[index1] = t[index1].integral_s(sabc)
                for index2 in [0, 1, 2]:
                    indexb = index2 - index1
                    if indexb < 0: indexb = indexb + 3
                    if indexb > 2: indexb = indexb - 3
                    integ[index1][index2] = fxx*t[index1].integral_dxdx(indexb) + \
                                            fyy*t[index1].integral_dydy(indexb) + \
                                              t[index1].integral_g(indexb, gabc)
                 
            source[i0] += s[0]    
            source[i1] += s[1] 
            source[i2] += s[2]
            amat[(i0,i0)] = amat.get((i0,i0),0.0) + integ[0][0]
            amat[(i0,i1)] = amat.get((i0,i1),0.0) + integ[0][1]
            amat[(i0,i2)] = amat.get((i0,i2),0.0) + integ[0][2]
            amat[(i1,i1)] = amat.get((i1,i1),0.0) + integ[1][1]
            amat[(i1,i2)] = amat.get((i1,i2),0.0) + integ[1][2]
            amat[(i1,i0)] = amat.get((i1,i0),0.0) + integ[1][0]
            amat[(i2,i2)] = amat.get((i2,i2),0.0) + integ[2][2]
            amat[(i2,i0)] = amat.get((i2,i0),0.0) + integ[2][0]
            amat[(i2,i1)] = amat.get((i2,i1),0.0) + integ[2][1]

        return [amat, source]


    def neumannB(self, nB, s):
        """
	Apply Neumann boundary conditions on the system of equations.
        """
        data = nB.getData()
        for pair in data:
            i = pair[0]
            j = pair[1]
            test = None
            for it in self.cells.data:
                if i in self.cells.data[it] and j in self.cells.data[it]:
                    for node in self.cells.data[it]:
                        if node != i and node != j:
                            test = self.cross(i,j,node)    
                    break        
            if test != None :
                sign = test/abs(test)
                xj,yj = self.grid.x(j),self.grid.y(j)
                xi,yi = self.grid.x(i),self.grid.y(i)
                a,b = xj - xi,yj - yi
                ds = sign*math.sqrt(a*a + b*b)
                A = data[pair]
                #integral contribution from i to j
                contrib = A*ds*(0.5) 
                s[i] = s[i] + contrib
                #integral contribution from j to i
                s[j] = s[j] + contrib


    def robinB(self,rB,amat,s):
        """
	Apply Robin boundary conditions on the system of equations.
	"""
        data = rB.getData()
        for pair in data:
            i = pair[0]
            j = pair[1]
            test = None
            for it in self.cells.data:
                if i in self.cells.data[it] and j in self.cells.data[it]:
                    for node in self.cells.data[it]:
                        if node != i and node != j:
                            test = self.cross(i,j,node)    
                    break        
            if test != None :
                sign = test/abs(test)
                xj,yj = self.grid.x(j),self.grid.y(j)
                xi,yi = self.grid.x(i),self.grid.y(i)
                a,b = xj - xi,yj - yi
                ds = sign*math.sqrt(a*a + b*b)
                A = data[pair][0]
                B = data[pair][1]
                
                #Changes to s vector:
                
                contrib = A*ds*(0.5)
                s[i] = s[i] + contrib
                s[j] = s[j] + contrib

                #Changes to the A matrix:

                Iij = B*ds*onesixth
                
                amat[(i,j)] = amat[(i,j)] + Iij
                amat[(j,i)] = amat[(j,i)] + Iij

                Iii = B*ds*(onethird)

                amat[(i,i)] = amat[(i,i)] + Iii

                Ijj = B*ds*(onethird)

                amat[(j,j)] = amat[(j,j)] + Ijj
    
    def cross(self,i,j,k):
        x1 = self.grid.x(j)-self.grid.x(i)
        y1 = self.grid.y(j)-self.grid.y(i)
        x2 = self.grid.x(k)-self.grid.x(i)
        y2 = self.grid.y(k)-self.grid.y(i)
        return (x1*y2 - x2*y1)
    

    def dirichletB(self,dB,amat,s):
        """
	Apply Dirichlet boundary conditions to the system of equations.
        """
        for ia in dB.getData():
            # set all off diagonal elements to zero
            # and diagonal to 1
            for ib in self.grid[ia][1]:
                del amat[(ia, ib)]
            amat[(ia, ia)] = 1.0                
            s[ia] = (dB.getData())[ia]    
    
			
    def toUCD(self, z, filename):
        """
	Write the solution to a UCD formatted file
        """
        f = open(filename, 'w')
        date = time.ctime( time.time() )
        f.write('# UCD format \n')
        f.write('# number_of_nodes number_of_cells \n')
        f.write('# nodes x y z \n')
        f.write('# cell_number class cell_type connection \n')
        f.write('# number_of_variables_per_node  number_of_variables_per_cell \n')
        f.write('# name_of_variable  units_of_variables \n')
        f.write('# node data \n')
        f.write('# '+date+'\n')
        f.write('1 \n') # only one time step
        f.write('data \n')
        f.write('step1 \n')
        ncells = len(self.cells.data)
        f.write(repr(len(self.grid.nodes()))+" "+repr(ncells)+" 1 \n")
        for node in self.grid.nodes():
                line = "%d %15.6e %15.6e 0.0 \n" % (node, self.grid.x(node), self.grid.y(node))
                f.write(line)
        for icell in range(ncells):
                f.write(repr(icell)+" 1  tri ")
                for node in self.cells.data[icell]:
                        f.write(repr(node)+' ')
                f.write('\n')
        f.write('1 0 \n') # 1 datum/per node 0 datum/cell
        f.write('1 1 \n') # 1 scalar per node
        f.write('v, m \n')
        for node in self.grid.nodes():
                line = "%d %15.6e \n" % (node, z[node])
                f.write(line)
        f.close()
