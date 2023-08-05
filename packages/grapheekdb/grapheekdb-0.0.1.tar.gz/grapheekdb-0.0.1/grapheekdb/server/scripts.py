# -*- coding:utf-8 -*-
"""
This module contains functions that can be called on the server side to create some side effects
Those functions are aimed to be called by the EntityIterator 'call' method
Each function MUST g and ctx as 2 first arguments
g is the graph
ctx is the "context" that is filled when EntityIterator 'as' method is used

From the client side it allows to build queries such as :
g.V().aka('x').outV(label='has_parent').outV(label='has_parent').aka('y').call('add_edge', 'x', 'y', label='has_grandparent')

The final call will :
- effectively be run by the server
- potentially have side effects on the graph

As you can see, in the call method, there's no need to pass 'g' and 'ctx' as those 2 variables are hold by the EntityIterator
The 'call' method will be in charge of looking for the right function and calling function passing g/ctx/ and other parameters
"""


def add_edge(g, ctx, ref1, ref2, **data):
    node1 = ctx[ref1]
    node2 = ctx[ref2]
    g.add_edge(node1, node2, **data)
