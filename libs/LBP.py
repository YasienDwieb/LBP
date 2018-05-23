import pandas as pd
import numpy as np
import networkx as nx
import decimal
import os
import sys
from decimal import *
import math
import aux_lbp as auxi
from networkx.drawing.nx_agraph import graphviz_layout
import plotly.plotly as py
from plotly.graph_objs import *
import plotly
import networkx as nx
import mysql.connector
from networkx_viewer import Viewer


#db_host='localhost'
#db_database='fraud'
#db_user='root'
#db_password='root'


def lbp(g):

#initial guess for messages (set them all to 1)    
    for (u,v) in g.edges():
        g[u][v]['mssd_h']=float(1)
        g[u][v]['mssd_a']=float(1)
        g[u][v]['mssd_f']=float(1)
        g[u][v]['msds_h']=float(1)
        g[u][v]['msds_a']=float(1)
        g[u][v]['msds_f']=float(1)
        g[u][v]['mssdO_h']=float(1)
        g[u][v]['mssdO_a']=float(1)
        g[u][v]['mssdO_f']=float(1)
        g[u][v]['msdsO_h']=float(1)
        g[u][v]['msdsO_a']=float(1)
        g[u][v]['msdsO_f']=float(1)
    
#compute degree of each node
    for u in g.nodes():
        g.node[u]['neighbours']=list(set(nx.edges_iter(g,nbunch=u)))
        g.node[u]['degree']=float(len(g.node[u]['neighbours']))
        
#compute sum of the weight.
    for u in g.nodes():
        n=g.node[u]['neighbours']
        suma=0
        for (h,w) in n:
            suma=suma+g[h][w]['weight']
        g.node[u]['sumweights']=float(suma)
    
# the prior for all the users (based on weight and degree)
    for u in g.nodes():
        g.node[u]['prior_h']=float(1)/(g.node[u]['sumweights']/g.node[u]['degree'])
        g.node[u]['prior_a']=g.node[u]['prior_f']=float((float(1)-g.node[u]['prior_h'])/2)
#         g.node[u]['prior_h']=g.node[u]['prior_a']=g.node[u]['prior_f']=float(0.333)

#compute propagation matrix values
    for (u,v) in g.edges():
        comp=auxi.propagation(g[u][v]['weight'],0.05)
        g[u][v]['c_ff']=float(comp[0])
        g[u][v]['c_fa']=float(comp[1])
        g[u][v]['c_fh']=float(comp[2])
        g[u][v]['c_af']=float(comp[3])
        g[u][v]['c_aa']=float(comp[4])
        g[u][v]['c_ah']=float(comp[5])
        g[u][v]['c_hf']=float(comp[6])
        g[u][v]['c_ha']=float(comp[7])
        g[u][v]['c_hh']=float(comp[8])

#set who is the source and who is the sink.
    for (u,v) in g.edges():
        g[u][v]['source']=u
        g[u][v]['dest']=v

# save the neighbours.
    for (u,v) in g.edges():
        g[v][u]['ns']=list(set(nx.edges_iter(g,nbunch=g[u][v]['source']))-set([(u,v)]))
        g[u][v]['nd']=list(set(nx.edges_iter(g,nbunch=g[u][v]['dest']))-set([(v,u)]))
        
#main loop: we iterate until the stopping criterion is reached on the  L-2 norm of the messages.
    tol=1
    numedges=len(g.edges())
    vector0=[float(10)]*numedges*6
    j=1
    
    while j<5:    
        
        vector=[]
        
        #message update from source to dest
        for (u,v) in g.edges():
            a=auxi.prods((u,v),'h',g)
            b=auxi.prods((u,v),'a',g)
            c=auxi.prods((u,v),'f',g)
            g[u][v]['mssd_h']=g[u][v]['c_hh']*g.node[g[u][v]['source']]['prior_h']*a+g[u][v]['c_ah']*g.node[g[u][v]['source']]['prior_a']*b+g[u][v]['c_fh']*g.node[g[u][v]['source']]['prior_f']*c
            g[u][v]['mssd_a']=g[u][v]['c_ha']*g.node[g[u][v]['source']]['prior_h']*a+g[u][v]['c_aa']*g.node[g[u][v]['source']]['prior_a']*b+g[u][v]['c_fa']*g.node[g[u][v]['source']]['prior_f']*c
            g[u][v]['mssd_f']=g[u][v]['c_hf']*g.node[g[u][v]['source']]['prior_h']*a+g[u][v]['c_af']*g.node[g[u][v]['source']]['prior_a']*b+g[u][v]['c_ff']*g.node[g[u][v]['source']]['prior_f']*c
            alpha=g[u][v]['mssd_h']+g[u][v]['mssd_a']+g[u][v]['mssd_f']
            g[u][v]['mssd_h']=g[u][v]['mssd_h']/alpha
            g[u][v]['mssd_a']=g[u][v]['mssd_a']/alpha
            g[u][v]['mssd_f']=g[u][v]['mssd_f']/alpha
            vector.append(g[u][v]['mssd_h'])
            vector.append(g[u][v]['mssd_a'])
            vector.append(g[u][v]['mssd_f'])
            
        #message update from dest to source
        for (u,v) in g.edges():
            a=auxi.prodd((u,v),'h',g)
            b=auxi.prodd((u,v),'a',g)
            c=auxi.prodd((u,v),'f',g)
            g[u][v]['msds_h']=g[u][v]['c_hh']*g.node[g[u][v]['dest']]['prior_h']*a+g[u][v]['c_ha']*g.node[g[u][v]['dest']]['prior_a']*b+g[u][v]['c_hf']*g.node[g[u][v]['dest']]['prior_f']*c
            g[u][v]['msds_a']=g[u][v]['c_ah']*g.node[g[u][v]['dest']]['prior_h']*a+g[u][v]['c_aa']*g.node[g[u][v]['dest']]['prior_a']*b+g[u][v]['c_af']*g.node[g[u][v]['dest']]['prior_f']*c
            g[u][v]['msds_f']=g[u][v]['c_fh']*g.node[g[u][v]['dest']]['prior_h']*a+g[u][v]['c_fa']*g.node[g[u][v]['dest']]['prior_a']*b+g[u][v]['c_ff']*g.node[g[u][v]['dest']]['prior_f']*c
            alpha=g[u][v]['msds_h']+g[u][v]['msds_a']+g[u][v]['msds_f']
            g[u][v]['msds_h']=g[u][v]['msds_h']/alpha
            g[u][v]['msds_a']=g[u][v]['msds_a']/alpha
            g[u][v]['msds_f']=g[u][v]['msds_f']/alpha
            vector.append(g[u][v]['msds_h'])
            vector.append(g[u][v]['msds_a'])
            vector.append(g[u][v]['msds_f'])
        
        #update old messages            
        for (u,v) in g.edges():
            g[u][v]['mssdO_h']=g[u][v]['mssd_h']
            g[u][v]['mssdO_a']=g[u][v]['mssd_a']
            g[u][v]['mssdO_f']=g[u][v]['mssd_f']
            g[u][v]['msdsO_h']=g[u][v]['msds_h']
            g[u][v]['msdsO_a']=g[u][v]['msds_a']
            g[u][v]['msdsO_f']=g[u][v]['msds_f']

        for u in g.nodes():
            g.node[u]['belief_h']=g.node[u]['prior_h']*auxi.prodnode(u,'h',g)
            g.node[u]['belief_a']=g.node[u]['prior_a']*auxi.prodnode(u,'a',g)
            g.node[u]['belief_f']=g.node[u]['prior_f']*auxi.prodnode(u,'f',g)
            alpha=g.node[u]['belief_h']+g.node[u]['belief_a']+g.node[u]['belief_f']
            g.node[u]['belief_h']=g.node[u]['belief_h']/alpha
            g.node[u]['belief_a']=g.node[u]['belief_a']/alpha
            g.node[u]['belief_f']=g.node[u]['belief_f']/alpha
            g.node[u]['prior_h']=g.node[u]['belief_h']
            g.node[u]['prior_a']=g.node[u]['belief_a']
            g.node[u]['prior_f']=g.node[u]['belief_f']
                  
        tol=np.linalg.norm(np.array(vector)-np.array(vector0),ord=2)
        vector0=vector    
        
        
        print j
        print tol
        j=j+1    


#compute final beliefs:    
    for u in g.nodes():
        g.node[u]['belief_h']=g.node[u]['prior_h']*auxi.prodnode(u,'h',g)
        g.node[u]['belief_a']=g.node[u]['prior_a']*auxi.prodnode(u,'a',g)
        g.node[u]['belief_f']=g.node[u]['prior_f']*auxi.prodnode(u,'f',g)
        alpha=g.node[u]['belief_h']+g.node[u]['belief_a']+g.node[u]['belief_f']
        g.node[u]['belief_h']=g.node[u]['belief_h']/alpha
        g.node[u]['belief_a']=g.node[u]['belief_a']/alpha
        g.node[u]['belief_f']=g.node[u]['belief_f']/alpha
              
#convert back to float:

    for u in g.nodes():
        g.node[u]['belief_h']=float(g.node[u]['belief_h'])
        g.node[u]['belief_a']=float(g.node[u]['belief_a'])
        g.node[u]['belief_f']=float(g.node[u]['belief_f'])
        g.node[u]['prior_h']=float(g.node[u]['prior_h'])
        g.node[u]['prior_a']=float(g.node[u]['prior_a'])
        g.node[u]['prior_f']=float(g.node[u]['prior_f'])
        
    for (u,v) in g.edges():
         g[u][v]['mssd_h']=float(g[u][v]['mssd_h'])
         g[u][v]['mssd_a']=float(g[u][v]['mssd_a'])
         g[u][v]['mssd_f']=float(g[u][v]['mssd_f'])
         g[u][v]['msds_h']=float(g[u][v]['msds_h'])
         g[u][v]['msds_a']=float(g[u][v]['msds_a'])
         g[u][v]['msds_f']=float(g[u][v]['msds_f'])       
         g[u][v]['c_ff']=float(g[u][v]['c_ff'])
         g[u][v]['c_fa']=float(g[u][v]['c_fa'])
         g[u][v]['c_fh']=float(g[u][v]['c_fh'])
         g[u][v]['c_af']=float(g[u][v]['c_af'])
         g[u][v]['c_aa']=float(g[u][v]['c_aa'])
         g[u][v]['c_ah']=float(g[u][v]['c_ah'])
         g[u][v]['c_hf']=float(g[u][v]['c_hf'])
         g[u][v]['c_ha']=float(g[u][v]['c_ha'])
         g[u][v]['c_hh']=float(g[u][v]['c_hh'])


    fraud_belief={}
    
    for u in g.nodes():
        fraud_belief[u]={'belief_f':g.node[u]['belief_f'], 'degree':len(g.node[u]['neighbours']),'sumweight':g.node[u]['sumweights']}

    users=pd.DataFrame.from_dict(fraud_belief,orient='index')
    users=users.reset_index()
    users.columns=['userid','belief_f','sumweight','degree']
    users = users.sort(['userid'], ascending=False)
    users[['userid']] = users[['userid']].astype(str)

    return users, j
  
def plotGraph(G,filename):  
  pos = graphviz_layout(G)
  for k in G.nodes():
    G.node[k]['pos']=pos[k]
    
  dmin=1
  ncenter=0
  for n in pos:
       x,y=pos[n]
       d=(x-0.5)**2+(y-0.5)**2
       if d<dmin:
           ncenter=n
           dmin=d
  
#  p=nx.single_source_shortest_path_length(G,ncenter)
  edge_trace = Scatter(
       x=[],
       y=[],
       line=Line(width=0.5,color='#888'),
       hoverinfo='text',
       text=[],
       textposition='top left',
       mode='lines+text')
  
  for edge in G.edges():
       x0, y0 = G.node[edge[0]]['pos']
       x1, y1 = G.node[edge[1]]['pos']
       edge_trace['x'] += [x0, x1, None]
       edge_trace['y'] += [y0, y1, None]
#       edge_trace['text'].append(G[edge[0]][edge[1]]['weight'])
       
  node_trace = Scatter(
       x=[],
       y=[],
       text=[],
       mode='markers+text',
       hoverinfo='none',
       showlegend='False',
       textposition='top center',
       marker=Marker(
           showscale=False,
           # colorscale options
           # 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
           # Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
           colorscale='YIGnBu',
           reversescale=True,
           color=[],
           size=15,
           colorbar=dict(
               thickness=15,
               title='Node Connections',
               xanchor='left',
               titleside='right'
           ),
           line=dict(width=2)))
  
  for node in G.nodes():
       x, y = G.node[node]['pos']
       node_trace['x'].append(x)
       node_trace['y'].append(y)
  
  for node in G.nodes():    
       if G.node[node]['belief_f']>0.5: 
         node_trace['marker']['color'].append('red')
       elif G.node[node]['belief_a']>0.5:
         node_trace['marker']['color'].append('yellow')       
       elif G.node[node]['belief_h']>0.5:
         node_trace['marker']['color'].append('green')
       url='Node '+str(node)+'<br><a href="http://localhost:8000/node/'+str(node)+'">More info</a>'
       node_trace['text'].append(url)
  
  fig = Figure(data=Data([edge_trace, node_trace]),
                layout=Layout(
                   title='<br>Fraud Detection',
                   titlefont=dict(
                       family='Droid Serif',
                       size=24
                   ),
                   showlegend=False,
                   hovermode='closest',
                   margin=dict(b=20,l=5,r=5,t=40),
                   annotations=[ dict(
                       text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                       showarrow=False,
                       xref="paper", yref="paper",
                       x=0.005, y=-0.002 ) ],
                   xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                   yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False),
                   font=dict(
                       family='Droid Serif',
                       size=14
                    ),
                 )
              )
  plotly.offline.plot(fig, filename=filename,auto_open=False)

def nodeFocused(G,nodeid):
  node_graph= nx.Graph()
  neighbors=G.node[nodeid]['neighbours']
  for (h,w) in neighbors:
    node_graph.add_edge(h,w)
    node_graph.node[h]['belief_f']=G.node[h]['belief_f']
    node_graph.node[h]['belief_h']=G.node[h]['belief_h']
    node_graph.node[h]['belief_a']=G.node[h]['belief_a']
    node_graph.node[w]['belief_f']=G.node[w]['belief_f']
    node_graph.node[w]['belief_h']=G.node[w]['belief_h']
    node_graph.node[w]['belief_a']=G.node[w]['belief_a']
  return node_graph


def loadBooks(host, database, user, password):
  cnx = mysql.connector.connect(user=user, password=password,
                            host=host,
                            database=database)
  cursor = cnx.cursor()
  
  query = ("SELECT * from books")
  
  cursor.execute(query)
  books=dict()
  for (id,title,imurl,user_id) in cursor:
    books[id]={}
    books[id]['title']=title
    books[id]['imurl']=imurl
    books[id]['user_id']=user_id
  cursor.close()
  cnx.close()
  return books

def loadTransactions(host, database, user, password):
  cnx = mysql.connector.connect(user=user, password=password,
                            host=host,
                            database=database)
  cursor = cnx.cursor()
  
  query = ("SELECT user_id,book_id FROM transactions group by user_id,book_id")
  
  cursor.execute(query)
  transactions=dict()
  for (user_id,book_id) in cursor:
    if user_id not in transactions:
      transactions[user_id]={}
    transactions[user_id][book_id]=1
  cursor.close()
  cnx.close()
  return transactions

# Gets raw records which will be used to extract information from.
def loadDBGraphDisconnected(host, database, user, password):
  books=loadBooks(host, database, user, password)
  G=nx.Graph()
  transactions=loadTransactions(host, database, user, password)
  for user in transactions.keys():
    G.add_node(user)
    for book in transactions[user]:
      user_to=books[book]['user_id']
      if ((user,user_to) not in G.edges()) and ((user_to,user) not in G.edges()):
        G.add_edge(user, user_to,weight=1)
      elif (user,user_to) in G.edges():
        G[user][user_to]['weight'] +=1
      elif (user_to,user) in G.edges():
        G[user_to][user]['weight'] +=1
  return G

# Performs an intensive SQL query to get needed values
def loadDBGraphConnected(host, database, user, password):
  cnx = mysql.connector.connect(user=user, password=password,
                            host=host,
                            database=database)
  cursor = cnx.cursor()

  G=nx.Graph()
  for user_from in range(1,110):
    for user_to in range(1,110):        
      query=('select count(*) as weight ' 
              ' from transactions,books ' 
              ' where ' 
              ' (transactions.book_id=books.id and books.user_id='+str(user_to)+' and transactions.user_id= '+str(user_from)+' ) '
              ' or ' 
              ' ( transactions.book_id=books.id and books.user_id='+str(user_from)+' and transactions.user_id= '+str(user_to)+' ) '
             )
      cursor.execute(query)
      for weight in cursor:
        G.add_edge(user_from, user_to,weight=weight[0])

  cursor.close()
  cnx.close()      
  return G

                            
#  
#datafile=pd.read_csv("csvfile.csv")
##  
#G=nx.from_pandas_dataframe(datafile, 'node1', 'node2', ['weight'])
#users,j=lbp(G)
#
##from enthought.mayavi import mlab
#
#if len(sys.argv)>1:
#  node=nodeFocused(G,int(sys.argv[1]))
#  plotGraph(node,'node')
#else:
#  plotGraph(G,'db')
#  nx.write_gpickle(G,'graph.pickle')


#app = Viewer(G)
#app.mainloop()
#   
#Graph=loadDBGraphDisconnected()
#users,j=lbp(Graph)
#plotGraph(Graph,'db')
#app = Viewer(Graph)
#app.mainloop()

#trace=open('trace.txt','w')
#for (u,v) in Graph.edges():
#  line='('+str(u)+','+str(v)+')'+'  '+str(Graph[u][v]['weight'])+'\n'
#  trace.write(line)
#  
#trace.close()

#Graph=loadDBGraphDisconnected()
#users,j=lbp(Graph)
#
#
#if len(sys.argv)>1:
#  node=nodeFocused(Graph,int(sys.argv[1]))
#  plotGraph(node,'node')
#else:
#  plotGraph(Graph,'db')
#  nx.write_gpickle(Graph,'graph.pickle')
#  app = Viewer(Graph)
#  app.mainloop()
