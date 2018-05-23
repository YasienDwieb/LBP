import pandas as pd
import numpy as np
import networkx as nx
import decimal
import os
import sys
from decimal import *
import math

#Complement functions to LBP.
###############################################################################
#This function computes the propagation matrix as defined in the Paper.

def propagation(w,ep=0.05):
    ff=float(ep)
    fa=float(1-2*ep)
    fh=float(ep)
    af=float(0.5)
    aa=float(2*ep)
    ah=float(0.5-2*ep)
    hf=float(ep)
    ha=float((1-ep)/2)
    hh=float((1-ep)/2)
    return (ff,fa,fh,af,aa,ah,hf,ha,hh)


###############################################################################
#Product of messages to the source.
#inputs:
#(u,v): an edge of a graph.
#c: the message sent (h for honest, s for sybil). In this case, c take values in
#{h,s} because we have a two-class network classification problem.
#g: the graph

def prods((u,v),c,g):
    s=g[u][v]['source']
    n=g[u][v]['ns']
    if len(n)==0:
        return 1
    elif c=='h':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==s:
                prod=float(prod)*float(g[h][w]['msdsO_h'])
            else:
                prod=float(prod)*float(g[h][w]['mssdO_h'])
    elif c=='a':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==s:
                prod=float(prod)*float(g[h][w]['msdsO_a'])
            else:
                prod=float(prod)*float(g[h][w]['mssdO_a'])
    elif c=='f':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==s:
                prod=float(prod)*float(g[h][w]['msdsO_f'])
            else:
                prod=float(prod)*float(g[h][w]['mssdO_f'])
    return prod

##############################################################################
#product of messages to dest

#inputs:
#(u,v): an edge of a graph.
#c: the message sent (h for honest, s for sybil)
#g: the graph

def prodd((u,v),c,g):
    d=g[u][v]['dest']
    n=g[u][v]['nd']
    if len(n)==0:
        return 1
    elif c=='h':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==d:
                prod=float(prod)*float(g[h][w]['msdsO_h'])
            else:
                prod=float(prod)*float(g[h][w]['mssdO_h'])
    elif c=='a':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==d:
                prod=float(prod)*float(g[h][w]['msdsO_a'])
            else:
                prod=float(prod)*float(g[h][w]['mssdO_a'])
    elif c=='f':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==d:
                prod=float(prod)*float(g[h][w]['msdsO_f'])
            else:
                prod=float(prod)*float(g[h][w]['mssdO_f'])
    return prod    

###############################################################################    
#product of all messages for a certain node.

#inputs:
#u: a node in the graph
#c: the message sent (h for honest, s for sybil)
#g: the graph

def prodnode(u,c,g):
    n=g.node[u]['neighbours']
    if c=='h':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==u:
                prod=float(prod)*float(g[h][w]['msds_h'])
            else:
                prod=float(prod)*float(g[h][w]['mssd_h'])
    elif c=='a':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==u:
                prod=float(prod)*float(g[h][w]['msds_a'])
            else:
                prod=float(prod)*float(g[h][w]['mssd_a'])
    elif c=='f':
        prod=1
        for (h,w) in n:
            if g[h][w]['source']==u:
                prod=float(prod)*float(g[h][w]['msds_f'])
            else:
                prod=float(prod)*float(g[h][w]['mssd_f'])
    return prod
    