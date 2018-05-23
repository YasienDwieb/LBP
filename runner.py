import networkx as nx
import sys
import pandas as pd
import os
import libs.LBP as LBP

#from optparse import OptionParser
#
#parser = OptionParser()
#parser.add_option("-f", "--file", dest="filename",
#                  help="File to process", metavar="FILE")
#parser.add_option("-d", "--database",
#                  action="store_false", dest="verbose", default=True,
#                  help="don't print status messages to stdout")
#
#(options, args) = parser.parse_args()


if len(sys.argv)>1:
  datafile=pd.read_csv(sys.argv[1])
  filename, file_extension = os.path.splitext(sys.argv[2])
  Graph=nx.from_pandas_dataframe(datafile, 'node1', 'node2', ['weight'])
  users,j=LBP.lbp(Graph)
  LBP.plotGraph(Graph,filename)
  nx.write_gpickle(Graph,filename+'.pickle')
  print 'Done'
else:
  print 'Please supply a valid filename'  