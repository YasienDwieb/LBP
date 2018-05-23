import networkx as nx
import sys
import libs.LBP
import os

if len(sys.argv)>1:
  G=nx.read_gpickle(sys.argv[1])
  filename, file_extension = os.path.splitext(sys.argv[1])
  node=LBP.nodeFocused(G,int(sys.argv[2]))
  LBP.plotGraph(node,str(filename)+'_'+str(sys.argv[2]))
else:
  print 'Not a valid node name'