import pandas as pd
import networkx as nx
# from enthought.mayavi import mlab
import libs.LBP as LBP
import sys
from networkx_viewer import Viewer

if len(sys.argv)>1:
	# usage: python runner_networkx.py file path_to_file
	if(sys.argv[1]=="file"):
		datafile=pd.read_csv(sys.argv[2])  
		G=nx.from_pandas_dataframe(datafile, 'node1', 'node2', ['weight'])
		users,j=LBP.lbp(G)
		app = Viewer(G)
		app.mainloop()
	elif(sys.argv[1]=="db"):
		# usage: python runner_networkx.py db localhost fraud root root
		db_host=sys.argv[2]
		db_database=sys.argv[3]
		db_user=sys.argv[4]
		db_password=sys.argv[5]
		Graph=LBP.loadDBGraphDisconnected(db_host,db_database,db_user,db_password)
		users,j=LBP.lbp(Graph)
		LBP.plotGraph(Graph,'db')
		app = Viewer(Graph)
		app.mainloop()
	else:
		print sys.argv[2]
else:
  print 'Please supply a valid an option either db or file'  
