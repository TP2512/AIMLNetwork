import networkx as nx
import pandas as pd
from pyvis.network import Network

nt = Network('600px', '1200px')

linked_list_df = pd.read_excel(
    r"C:\Users\tpujari\Desktop\infrastructuresvg\VIProject\Network_Analysis\Data\ll_test_single_net.xlsx",
    usecols=['source', 'target'])
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)
# Create a graph
Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)
# sub_graphs = nx.connected_components(G)
betweenness = nx.betweenness_centrality(G)
print("Betweenness")
for node, value in betweenness.items():
    print(node, value)
# nt.from_nx(G)
# nt.show('nx.html', notebook=False)
print("closeness")
closeness = nx.closeness_centrality(G)
for node, value in closeness.items():
    print(node, value)

for i in G.nodes:
    print(f"node : {i} :: degree: {nx.degree(G, i)}")

node1 = 'a7'
node2 = 'a4'
common_neighbors = list(nx.common_neighbors(G, node1, node2))
print(f"common neighbours of {node1} and {node2} is {common_neighbors}")
