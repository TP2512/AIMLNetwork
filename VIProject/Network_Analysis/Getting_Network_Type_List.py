import pandas as pd
import networkx as nx
from pyvis.network import Network
import os
import matplotlib.pyplot as plt

def update_source_target(row):
    if row['so_nssid'] in nssid_info['NSSID'].tolist():
        row['source'] += '_GNE'
    if row['si_nssid'] in nssid_info['NSSID'].tolist():
        row['target'] += '_GNE'
    return row


nssid_info = pd.read_excel(r"Data\nssid.xlsx",usecols=['NSSID'])
nssid_info.dropna(inplace=True)
nssid_info['NSSID'] = nssid_info['NSSID'].apply(lambda x: x.strip())

links = pd.read_excel(r"Data\link_list_odi.xlsx",usecols=['NEAlias', 'FarEndNEName'])
links.dropna(inplace=True)
links.rename({'NEAlias': 'source', 'FarEndNEName': 'target'}, axis=1, inplace=True)
links['links'] = links['source'] + '-' + links['target']
links.drop_duplicates(['links'],keep='first', inplace=True)
links["so_nssid"] = links.source.str.split('_|-', n=1, expand=True)[0]
links["si_nssid"] = links.target.str.split('_|-', n=1, expand=True)[0]
links = links.apply(update_source_target, axis=1)
# links.to_excel("links.xlsx")

Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(links, create_using=Graphtype)
# G.add_nodes_from(node_names)

sub_graphs = nx.connected_components(G)
# for i, sg in enumerate(sub_graphs):
#     print('main graphs',sg)
#     #plot graph
#     nt = Network('600px', '1200px')
#     nt.from_nx(G)
#     nt.show('nx.html', notebook=False)
for i, subgraph_nodes in enumerate(sub_graphs):
    subgraph = G.subgraph(subgraph_nodes)
    net = Network(notebook=False)

    # Add nodes and edges to the visualization
    for node in subgraph.nodes:
        net.add_node(node)
    for edge in subgraph.edges:
        net.add_edge(edge[0], edge[1])

    # Set a title for the visualization (optional)
    gne_nodes = [node for node in subgraph.nodes if "GNE" in node]
    all_nodes = list(G.nodes)
    try:
        html_filename = os.path.join("Graphs", f'subgraph_{gne_nodes[0]}.html')
    except:
        html_filename = os.path.join("Graphs", f'subgraph_{all_nodes[0]}.html')


    # Save the visualization as an HTML file (optional)
    net.save_graph(html_filename)

print("task complete")
