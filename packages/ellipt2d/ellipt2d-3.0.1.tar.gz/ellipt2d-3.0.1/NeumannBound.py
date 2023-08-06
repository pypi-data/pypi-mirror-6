#!/usr/bin/env python
# $Id: NeumannBound.py,v 1.6 2013/12/20 22:45:35 pletzer Exp $
#
# treats the Neumann boundary conditions
# J. Mollis 27 Jun 2000
"""
ellipt2d: data structure to hold Neumann boundary conditions
"""

from types import *

class NeumannBound:
    """
    Stores and manages all boundary edges requiring *generalized*
    Neumann boundary conditions of the form:

    n*F*grad(v) = alpha

    *Note* that the above BCs differ from the usual Neumann
    boundary conditions n.grad v = alpha by the tensor F! 
    
    Data Structure (a dictionary): { (i1,i2): n*F*grad(v) ,...}
    (i1,i2) represents a line segment from node number i1 to i2
    Methods with NeumannBound object as an argument:

    ellipt2d.neumannB(<nB Object>,<sparse class>,<vector class>)

    Unlike DirichletBound there is no simple interface with Ireg2tri
    to specify boundary edges. One must use the methods:

    Ireg2tri.setAttributes(self,<dictionary>)
    <dictionary> = { <node number> : [<Boundary marker: 0 or 1>,<dB value>,<A>,<B>] ...}
    Ireg2tri.getAttributes(self) (returns a dictionary of the same form)
    Points will most likely be added to the boundary and interpolation of all
    attributes will occur.
    
    """
    def __init__(self,start = {}):
        """
        Initializes the dictionary data strucuture member
        Defaults to Empty dictionary if no arguments are supplied.
        """
        if type(start) == DictType:
            self.data = start              
        else:
            raise TypeError(self.__class__).with_traceback('in __init__')

    def __setitem__(self,pair,nFgradv):
        """
        Data setting function, Overridden from Object class.
        Usage: <NeumannBound Object>[(i1,i2)] = <n*F*grad(v)>
        If the edge specified is not already in the dictionary
        then it will be added. 
        """
        if type(pair) == TupleType:
            self.data[pair] = nFgradv
        else:
            raise TypeError(self.__class__).with_traceback('in __setitem__')

    def __getitem__(self,pair):
        """
        Data access function, Overridden from Object class
        Usage: x = <NeumannBound Object>[(i1,i2)]
        None returned on failure,
        Otherwise the value of n*F*grad(v) at edge (i1,i2) is returned
        """
        if type(pair) == TupleType:
            try:
                return self.data[pair]
            except:
                return None
        else:
            raise TypeError(self.__class__).with_traceback('in __getitem__')

    def isBound(self,pair):
        """
        Returns greater than 1 if the edge specified corresponds to a
        edge with Neumann boundary conditions
        Returns 0 otherwise
        """
        return (pair in list(self.data.keys())) # >= 1 for true, 0 for false
        
    def out(self):
        """
        Prints the dictionary data structure: <(i,j)> <n*F*grad(v)>
        """
        print('Edge value of n*F*grad(v)','\n')
        for x in list(self.data.keys()):
            print(x , self.data[x])

    def __del__(self):
	"""
	Frees the memory associated with the NeumannBound data structure.
	"""
	del(self.data)

    def getData(self):
        """
        Returns the dictioary data structure
        """
        return self.data

    def areConnected(self,grid):
        """
        Determines if the current data structure contains only connected
        adjacent nodes (this must be the case for proper operation).
        Upon success, 1 is returned, otherwise 0 is returned. This method
        can be used to check the alidity of the NeumannBound object.
        """
        for pairs in list(self.data.keys()):
            if pairs[1] not in grid.linkedNodes(pairs[0]):
                return 0
        return 1


    def isNeumannBound(self):
        """
        Object introspection: return 1
        """
        return 1
    
        
    def plot(self,grid,tag=0,WIDTH = 400,HEIGHT = 400):
        """
        Plots all Neumann boundary edges, connecting nodes irrespective of the
        fact that only adjacent nodes can be connected.
        tag = 0 (no edge tags), tag = 1 (edge tags)
        """

        try:
            from tkinter import Tk, Frame, Button, Canvas, BOTTOM, Label
        except:
            from Tkinter import Tk, Frame, Button, Canvas, BOTTOM, Label

        OFFSET = 0.05*min([WIDTH, HEIGHT])
        EPS = 4
        [xmin, ymin, xmax, ymax] = grid.boxsize()
        SCALE = min([0.9*WIDTH, 0.9*HEIGHT])/max([xmax-xmin, ymax-ymin])
        root = Tk()
        frame = Frame(root)
        frame.pack()
        button = Button(frame, text="OK", fg="red", command=frame.quit)
        button.pack(side=BOTTOM)
        canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT)
        canvas.pack()
        text = Label(width=30, height=10, text='Neumann Boundary Edges')
        text.pack()
        a,b = 0,0
        if SCALE*xmin < OFFSET:
            a = abs(SCALE*xmin) + OFFSET
        if SCALE*xmax > WIDTH - OFFSET:
            a = -(SCALE*xmax - WIDTH + OFFSET)
        if SCALE*ymin < OFFSET:
            b = abs(SCALE*ymin)+OFFSET
        if SCALE*ymax > HEIGHT-OFFSET:
            b = -(SCALE*ymax - HEIGHT + OFFSET)
        for pairs in list(self.data.keys()):
                    x1, y1 = SCALE*grid.x(pairs[0])+a, HEIGHT-SCALE*grid.y(pairs[0])-b
                    x2, y2 = SCALE*grid.x(pairs[1])+a, HEIGHT-SCALE*grid.y(pairs[1])-b
                    canvas.create_line(x1, y1, x2, y2)
                    if tag == 1: canvas.create_text(x1+EPS, y1-EPS, text=str(pairs))
        root.mainloop()
        
        
