import networkx as nx
import sys
import LBP
import os

if len(sys.argv)>1:
  G=nx.read_gpickle(sys.argv[1])
  filename, file_extension = os.path.splitext(sys.argv[1])
  LBP.plotGraph(G,filename)
else:
  print 'Not a valid pickle file'