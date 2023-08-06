#!/usr/env python

# $Id: test_supralu.py,v 1.1 2005/11/27 20:52:28 pletzer Exp $

"""
Performance test 
"""

import sys
import dsupralu

# size of problem
n = 10000
if len(sys.argv) > 1:
    n = int(sys.argv[1])

# number of times problem is solved (for reference check count)
m = 2
if len(sys.argv) > 2:
    m = int(sys.argv[2])

for j in range(m):
    a = {}
    for i in range(n-1):
        a[(i  ,i  )] = 3.0
        a[(i+1,i  )] = 2.0
        a[(i  ,i+1)] = 1.0
    a[(n-1,n-1)] = 3.0

    b = [0 for i in range(n)]
    b[0] = 1.0

    h1, h2 = dsupralu.new(a, n)
    colperm = 2
    dsupralu.colperm(h1, colperm)
    dsupralu.lu(h1)
    dsupralu.SOLVE(h1, b)

    print 'checksum: %20.15g ' % reduce(lambda x,y: x+y, b)

      
