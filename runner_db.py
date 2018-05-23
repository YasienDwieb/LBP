import networkx as nx
import sys
import libs.LBP as LBP

if len(sys.argv)>1:
  db_host=sys.argv[1]
  db_database=sys.argv[2]
  db_user=sys.argv[3]
  db_password=sys.argv[4]
  Graph=LBP.loadDBGraphDisconnected(db_host, db_database, db_user, db_password)
  users,j=LBP.lbp(Graph)
  LBP.plotGraph(Graph,sys.argv[5])
  nx.write_gpickle(Graph,sys.argv[5]+'.pickle')
  print 'Done'
else:
  print 'Invalid database'