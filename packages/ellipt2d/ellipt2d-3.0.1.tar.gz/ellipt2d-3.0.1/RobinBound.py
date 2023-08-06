#!/usr/bin/env python
# $Id: RobinBound.py,v 1.3 2013/12/20 22:45:35 pletzer Exp $
#
# treats the Robin boundary conditions
# J. Mollis 27 Jun 2000
"""
ellipt2d: data structure to hold Robin boundary conditions
"""

from types import *

class RobinBound:
    """
    Stores and manages all boundary edges requiring
    Robin boundary conditions. If a case degenerates to Neumann or Dirichlet
    boundary conditions then those classes should be used.
    
    Data Structure(a dictionary): { (i1,i2): (A,B) }
    
    A and B are defined as follows:

    n*F*grad(v) = A - B v

    Methods with RobinBound object as an argument:

    ellipt2d.robinB(<rB Object>,<sparse class>,<vector class>)

    Interfacing with Ireg2tri is the same as for NeumannBound objects.
    
    """
    def __init__(self,start = {}):
        """
        Initializes the dictionary data structure member
        Defaults to Empty dictionary if no arguments are supplied.
        """

        if type(start) == DictType:
            self.data = start              
        else:
            raise TypeError(self.__class__).with_traceback('in __init__')

    def __setitem__(self,pair,data):
        """
        Data setting function, Overridden from Object class.
        Usage: <RobinBound Object>[(i1,i2)] = (A,B)
        If the edge specified is not already in the dictionary
        then it will be added to the dictionary.
        """
        if type(pair) == TupleType:
            self.data[pair] = data
        else:
            raise TypeError(self.__class__).with_traceback('in __setitem__')

    def __getitem__(self,pair):
        """
        Data access function, Overridden from Object class.
        Usage: x = <RobinBound Object>[(i1,i2)]
        None returned on failure.
        Otherwise (A,B) at edge (i1,i2) is returned.
        """
        if type(pair) == TupleType:
            try:
                return self.data[pair]
            except: return None
        else:
            raise TypeError(self.__class__).with_traceback('in __getitem__')

    def isBound(self,pair):
        """
        Returns 1 if the edge specified corresponds to a
        edge with Robin boundary conditions.
        Returns 0 otherwise.
        """
        return (pair in list(self.data.keys()))        

    def out(self):
        """
        Prints the dictionary data structure: <(i,j)> <n*F*grad(v)>
        """
        print('Edge values for n*F*grad(v) = A - B*V')
        for x in list(self.data.keys()):
	    print(x , self.data[x])    

    def __del__(self):
	"""
	Free's the memory associated with the RobinBound data structure.
	"""
	del(self.data)


    def getData(self):
        """
        Returns the dictionary data structure.
        """
        return self.data

    def areConnected(self,grid):
        """
        Determines if the current data structure contains only connected
        adjacent nodes(This must be the case for proper operation).
        Upon success, 1 is returned, otherwise 0 is returned. This method
        can be used to validate the RobinBound object.
        """
        for pairs in list(self.data.keys()):
            if pairs[1] not in grid.linkedNodes(pairs[0]):
                return 0
        return 1

    def isRobinBound(self):
        """
        Object introspection: return 1
        """
        return 1
    
    
    def plot(self,grid,tag=0,WIDTH = 400,HEIGHT = 400):
        """
        Plots all Robin boundary edges, connecting nodes irrespective of the
        fact that only adjacent nodes can be connected.
        tag = 0 (no edge tags), tag = 1 (edge tags) 
        """

        try:
            from tkinter import Tk, Frame, Label, Button, Canvas, BOTTOM # python 3
        except:
            from Tkinter import Tk, Frame, Label, Button, Canvas, BOTTOM # python 2

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
        text = Label(width=30, height=10, text='Robin Boundary Edges')
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

