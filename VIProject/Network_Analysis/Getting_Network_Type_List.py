import pandas as pd
import networkx as nx
from pyvis.network import Network
import os
import matplotlib.pyplot as plt

linked_list_df = pd.read_excel(r"Data\ll_test_single_net.xlsx",usecols=['source', 'target'])
no_of_rows=linked_list_df.shape[0] #get number of rows
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)

Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)

sub_graphs = nx.connected_components(G)
list_of_networks = pd.DataFrame()
list_of_net = []
for i, sg in enumerate(sub_graphs):
    print('main graphs',sg)
    list_of_net.append(sg)

list_of_networks.insert(0, "listofnetwork", list_of_net)
list_of_networks.to_excel(r"Data\test_networkx.xlsx")
print("group finding complete")

#plot graph
nt = Network('600px', '1200px')
nt.from_nx(G)
nt.from_nx(G)
nt.show('nx.html', notebook=False)

rings_in_network=list(nx.simple_cycles(G))
print("rings_in_network",rings_in_network)

