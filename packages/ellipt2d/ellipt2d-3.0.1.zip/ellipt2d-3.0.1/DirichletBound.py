#!/usr/bin/python
# $Id: DirichletBound.py,v 1.4 2013/12/20 22:45:35 pletzer Exp $
#
# treats the Dirichlet boundary conditions
# J. Mollis 27 Jun 2000
"""
ellipt2d: data structure to hold Dirichlet boundary conditions
"""


from types import *

class DirichletBound:
    """
    Stores all boundary points that require Dirichlet boundary conditions.

    Data structure: self.data = { <index> : <boundary value> }
    <index> represents a node number
    Methods with DirichletBound object as an argument:
   
    Ireg2tri.setUpDirichlet(<dB Object>)
    Ireg2tri.updateDirichlet(<dB Object>)
    ellipt2d.dirichletB(<dB Object>,<sparse class>,<vector class>)
    """
    def __init__(self, start = {} ):
        """
        Initializes the dictionary data structure member.
        Defaults to Empty dictionary if no arguments are supplied.
        """
        if type(start) == DictType:
            self.data = start              
        else:
            raise TypeError(self.__class__).with_traceback('in __init__')

    def __getitem__(self,i):
        """
        Data access function, Overridden from Object class.
        Usage: x = <DirichletBound Object>[<index>]
        None returned on failure.
        Otherwise the Boundary value at node numbered <index> is returned.
        """
        if i in list(self.data.keys()):
            return self.data[i]
        else: return None

    def __setitem__(self,i,nodeInfo):
        """
        Data setting function, Overridden from Object class.
        Usage: <DirichletBound Object>[<index>] = <boundary value>
        If the node number specified is not already in the dictionary
        then it will be added to the dictionary.
        """
        self.data[i] = nodeInfo

    def __setslice__(self,i,j,v):
        """
        A simplified slice operation.
        Usage: <DirichletBound Object>[<start index> :<end index>] = <boudnary value>
        Slice will include the ending index.
        If the node number specified is not already in the dictionary
        then it will be added to the dictionary.
        """
        for inode in range(i,j+1):
            try:
                self.data[inode] = v
            except:
                pass
    def getData(self):
        """
        Returns the DataStructure dictionary.
        """
        return self.data

    def setData(self,data):
        """
        Sets the data dictionary to be equal to the argument.
        If a dictionary is not sent a TypeError is raised.
        """
        if type(data) == DictType:
            self.data = data              
        else:
            raise TypeError(self.__class__).with_traceback('in setData(...)')

    def isBound(self,i):
        """
        Returns 1 if the node number specified corresponds to a
        node with Dirichlet boundary conditions.
        Returns 0 otherwise.
        """
        return (i in list(self.data.keys())) # returns 0 for no and 1 for yes.

    def out(self):
        """
        Prints the dictionary data strucuture: <node number> <boundary value>
        """
        print('node  Boundary Value')
        for x in list(self.data.keys()):
            print(x , self.data[x])
    
    def __del__(self):
	"""
	Free's the memory associated with the DirichletBound data structure.
	"""
	del(self.data)

    def isDirichletBound(self):
        """
        Object introspection: return 1
        """
        return 1

    def plot(self,grid,tag=0,WIDTH = 400,HEIGHT = 400):
        """
        Plots all Dirichlet boundary points, assuming that if connections
        can be made they will be.
	tag = 0 (no node numbers), tag = 1 (node numbers)
        """

        try:
            from tkinter import Tk, Frame, Button, Canvas, BOTTOM, Label # python 3
        except:
            from Tkinter import Tk, Frame, Button, Canvas, BOTTOM, Label # python 2
            
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
        text = Label(width=30, height=10, text='Dirichlet Boundary Nodes')
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
        for i in list(self.data.keys()):
            x1, y1 = SCALE*grid.x(i)+a, HEIGHT-SCALE*grid.y(i)-b
            canvas.create_oval(x1,y1,x1,y1)
            if tag == 1: canvas.create_text(x1+EPS, y1-EPS, text=str(i))
        root.mainloop()

if __name__ == "__main__":
    b = DirichletBound()

    
    












    
        
