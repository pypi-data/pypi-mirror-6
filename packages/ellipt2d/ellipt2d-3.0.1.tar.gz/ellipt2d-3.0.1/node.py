#!/usr/bin/env python
# $Id: node.py,v 1.6 2013/12/20 22:38:27 pletzer Exp $
#

"""
ellipt2d: node connectivity data structure
"""

from types import *

class node:
    """
    Stores and manages all mesh nodes and connections.
    Node data structure { <index> : [ <(x,y)>,<connections:[i1,i2,i3,...]>, <boundary attribute: 0 or 1> ] }
    <index> is the node number. The first element is a tuple with the x-y coordinates of the node, the
    second element is a list of node number that <index> is connected to and the last is 0 for off the
    boundary and 1 for on the boundary.
    Methods with node as an argument:

    NeumannBound.plot(self,<node object>,tag=0,WIDTH = 400,HEIGHT = 400)
    DirichletBound.plot(self,<node object>,tag=0,WIDTH = 400,HEIGHT = 400)
    RobinBound.plot(self,<node object>,tag=0,WIDTH = 400,HEIGHT = 400)
    ellipt2d.__init__(self, <node object>, f_funct_str, g_funct_str, s_funct_str):
    
    """
    
    def __init__(self, start={}):
        """
        Initializes the dictionary data structure member
        Defaults to Empty dictionary if no arguments are supplied.
        
        """
        if type(start) == DictType:
            self.data = start
        else:
            raise TypeError(self.__class__).with_traceback('in __init__')

    def set(self, inode, coordinates):
        """
        Sets the coordinates of node numbered inode, the connection list to an empty list
        and the boundary attribute to 0.
        """
        self.data[inode] = [coordinates,[],0]

    def setBound(self,inode):
        """
        Sets the boundary attribute fo node numbered inode to 1(on the boundary)
        """
        self.data[inode][2] = 1  

    def isBound(self,inode):
        """
        Determines if node numbered inode is on the boundary. If so, 1 is returned.
        Otherwise 0 is returned.
        """
        if (self.data[inode][2] == 1): return 1
        else: return 0

    def connect(self, inode1, inode2):
        """
        Connects nodes numbered inode1 and inode2 by adding one to the others list of
        connections.
        """
        if type(inode1)==IntType and type(inode2)==IntType:
            self.data[inode1][1].append(inode2)
        else:
            raise TypeError(self.__class__).with_traceback('in connect')

    def disconnect(self, inode1, inode2):
        """
        Disconnects nodes numbered inode1 and inode2 by removing one from the others list
        of connections.
        """
        if type(inode1)==IntType and type(inode2)==IntType:
            self.data[inode1][1].remove(inode2)
        else:
            raise TypeError(self.__class__).with_traceback('in disconnect')
        
    def isConnected(self, inode1, inode2):
        """
        Determines if nodes numbered inode1 and inode2 are connected.
        If so 1 is returned. Otherwise 0 is returned.
        """
        if type(inode1)==IntType and type(inode2)==IntType:
            return inode2 in self.data[inode1][1]
        else:
            raise TypeError(self.__class__).with_traceback('in connect')

    def setData(self,data):
        """
        Sets the dictionary data structure to be equal to the dictionary
        referenced by data.
        """
        if type(data) == DictType:
            self.data = data
        else:
            raise TypeError(self.__class__).with_traceback('in setData')

    def __del__(self):
        """
        Overidden delete operation, called automatically during garbage collections
        or upon request.
        """
        del self.data

    def __len__(self):
        """
        returns the length of the dictionary data structure.
        """
        return len(self.data)

    def __getitem__(self, inode):
        """
        Overided get item function.
        Returns the node numbered inode if it exists and None otherwise.
        """
        if type(inode)==IntType:
            return self.data[inode]
        else:
           raise TypeError(self.__class__).with_traceback('in __getitem__')

    def nodes(self):
        """
        Returns a list of the node numbers.
        """
        return list(self.data.keys())
    
    def linkedNodes(self, inode):
        """
        Returns a list of the node numbers of nodes connected to node
        numbered inode.
        """
        return self.data[inode][1]
    
    def out(self):
        """
        Prints out the dictionary data structure: <node number>  [(x, y), [connections]]
        """
        print('# node : [(x, y), connections]')
        for inode in list(self.data.keys()):
            print(inode, self.data[inode])

    def x(self, inode):
        """
        Returns the x coordinate of node numbered inode.
        """
        return self.data[inode][0][0]

    def y(self, inode):
        """
        Returns the y coordinate of node numbered inode.
        """
        return self.data[inode][0][1]

    def boxsize(self):
        """
        Returns a list denoting a box that contains the entire structure of nodes
        Structure: [xmin, ymin, xmax, ymax] 
        """
        large = 1000.0
        xmin= large
        xmax=-large
        ymin= large
        ymax=-large
        for inode in list(self.data.keys()):
            if self.data[inode][0][0] < xmin:
                xmin = self.data[inode][0][0]
            if self.data[inode][0][0] > xmax:
                xmax = self.data[inode][0][0]
            if self.data[inode][0][1] < ymin:
                ymin = self.data[inode][0][1]
            if self.data[inode][0][1] > ymax:
                ymax = self.data[inode][0][1]
        return [xmin, ymin, xmax, ymax]


    def plot(self,tag = 0,WIDTH = 400,HEIGHT = 400):
        """
        Plots all node connections.
        tag = 0 (no node numbers), tag = 1 (node numbers)
        """

        try:
            from tkinter import Tk, Frame, Button, Canvas, BOTTOM, Label
        except:
            from Tkinter import Tk, Frame, Button, Canvas, BOTTOM, Label
            
            OFFSET = 0.05*min([WIDTH, HEIGHT])
            EPS = 4
            [xmin, ymin, xmax, ymax] = self.boxsize()
            SCALE = min([0.9*WIDTH, 0.9*HEIGHT])/max([xmax-xmin, ymax-ymin])
            root = Tk()
            frame = Frame(root)
            frame.pack()
            button = Button(frame, text="OK", fg="red", command=frame.quit)
            button.pack(side=BOTTOM)
            canvas = Canvas(bg="white", width=WIDTH, height=HEIGHT)
            canvas.pack()
            text = Label(width=10, height=10, text='grid')
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
            for inode in list(self.data.keys()):
                for inode2 in self.data[inode][1]:
                    x1, y1 = SCALE*(self.x(inode )) + a,  HEIGHT-SCALE*(self.y(inode )) - b 
                    x2, y2 = SCALE*(self.x(inode2)) + a,  HEIGHT-SCALE*(self.y(inode2)) - b 
                    canvas.create_line(x1, y1, x2, y2)
                    if tag == 1 : canvas.create_text(x1+EPS, y1-EPS, text=str(inode))
            root.mainloop()

        
    def getBoundNodes(self):
        BNodes = []
        for inode in list(self.data.keys()):
            if( self.data[inode][2] == 1 ):
                BNodes.append(inode)
        return BNodes

     
        
###############################################################################
if __name__ == "__main__":

   
    
    xmin = 0.0
    xmid = 1.0
    xmax = 2.0
    ymin = 0.0
    ymid = 1.0
    ymax = 2.0
    

    mygrid = node({})
    print('set node coordinates')
    mygrid.set(0, (xmin, ymin))
    mygrid.set(1, (xmax, ymin))
    mygrid.set(2, (xmid, ymid))
    mygrid.set(3, (xmin, ymax))
    mygrid.set(4, (xmax, ymax))

    print('connect nodes')
    mygrid.connect(0,1)
    mygrid.connect(0,2)
    mygrid.connect(0,3)

    mygrid.connect(1,4)
    mygrid.connect(1,2)
    mygrid.connect(1,0)

    mygrid.connect(2,4)
    mygrid.connect(2,3)
    mygrid.connect(2,1)
    mygrid.connect(2,0)
    
    mygrid.connect(3,0)
    mygrid.connect(3,2)
    mygrid.connect(3,4)
    
    mygrid.connect(4,1)
    mygrid.connect(4,2)
    mygrid.connect(4,3)

    print('mygrid.isConnected(4,3)=',mygrid.isConnected(4,3))
    print('mygrid.isConnected(4,0)=',mygrid.isConnected(4,0))
   
    print('box size is ', mygrid.boxsize())
    
    mygrid.out()

    mygrid.plot()



    
