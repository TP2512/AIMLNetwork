import networkx as nx
import pandas as pd
import itertools
import time
from pyvis.network import Network
import os
def update_source_target(row):
    if row['so_nssid'] in nssid_info['NSSID'].tolist():
        row['source'] += '_GNE'
    if row['si_nssid'] in nssid_info['NSSID'].tolist():
        row['target'] += '_GNE'
    return row

nssid_info = pd.read_excel(r"nssid.xlsx",usecols=['NSSID'])
nssid_info.dropna(inplace=True)
nssid_info['NSSID'] = nssid_info['NSSID'].apply(lambda x: x.strip())

links = pd.read_excel(r"link_list.xlsx",usecols=['NEAlias', 'FarEndNEName'])
links.dropna(inplace=True)
links.rename({'NEAlias': 'source', 'FarEndNEName': 'target'}, axis=1, inplace=True)
links['links'] = links['source'] + '-' + links['target']
links.drop_duplicates(['links'],keep='first', inplace=True)
links["so_nssid"] = links.source.str.split('_|-', n=1, expand=True)[0]
links["si_nssid"] = links.target.str.split('_|-', n=1, expand=True)[0]
links = links.apply(update_source_target, axis=1)
links.to_excel("links.xlsx")

dt = pd.DataFrame([])
dt = pd.concat([links["source"], links["target"]], axis=0, ignore_index=True)
dt = dt.drop_duplicates()
node_names = dt.to_list()

Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(links, create_using=Graphtype)
G.add_nodes_from(node_names)
sub_graphs = nx.connected_components(G)

main_nw_graph_type=[]
name_of_gne=[]
down_link=[]
dep_nodes=[]
main_graph=[]
sub_graph_list=[]
no_of_gne=[]
nw_type=[]
c=0
gr_no=[]
all_paths = []
gne_list = []
link_list = []
path_list = []
for i, sg1 in enumerate(sub_graphs):
    # print("main_graph",list(sg1))
    subgraph = G.subgraph(sg1)
    c += 1
    new_graph = subgraph.copy()
    try:
        nx.find_cycle(subgraph)
        main_nw_graph_type_str="Mesh"
    except:
        main_nw_graph_type_str="Spur"
    gne_nodes = [node for node in new_graph.nodes if "GNE" in node]
    no_gnes=len(gne_nodes)
    node_groups = {gne_node: set([gne_node]) for gne_node in gne_nodes}
    for node in new_graph.nodes:
        if "GNE" not in node:
            shortest_distances = {
                gne_node: nx.shortest_path_length(new_graph, node, gne_node) for gne_node in gne_nodes
            }
            try:
                min_distance = min(shortest_distances.values())
            except ValueError:
                min_distance=0
            closest_gne_nodes = [gne_node for gne_node, distance in shortest_distances.items() if
                                 distance == min_distance]
            for gne_node in closest_gne_nodes:
                node_groups[gne_node].add(node)

    for ng,sg in node_groups.items():
        subgraph = G.subgraph(sg)
        gne_llst = [j for j in sg if "_GNE" in j]
        gne_node = gne_llst[0]
        new_graph_gne = subgraph.copy()
        # print(new_graph_gne.edges())
        source_node = gne_node

        for edge in new_graph_gne.edges():
            new_graph_gne.remove_edge(*edge)
            path_len = []
            if source_node in edge:
                # print(edge, source_node, edge)
                path_len.append(0)
                link_list.append(edge)
                gne_list.append(source_node)
                path_list.append(edge)
                nw_type.append(main_nw_graph_type_str)
            for target_node in edge:
                paths = list(nx.all_simple_edge_paths(new_graph_gne, source=source_node, target=target_node))
                for path in paths:
                    path_len.append(len(path))
                    link_list.append(edge)
                    gne_list.append(source_node)
                    path_list.append(path)
                    nw_type.append(main_nw_graph_type_str)
                    # print(edge, source_node, path)
            link_list.append(edge)
            gne_list.append(f"{source_node}-summary")
            path_list.append(path_len)
            # print(f"summary-{edge} {sorted(path_len)}")
            new_graph_gne.add_edge(*edge)
            nw_type.append(main_nw_graph_type_str)

list_of_edges=pd.DataFrame()
list_of_edges.insert(0, "Network Type", nw_type)
list_of_edges.insert(1, "GNE", gne_list)
list_of_edges.insert(2, "Link", link_list)
list_of_edges.insert(3, "Path", path_list)
list_of_edges.to_excel("network_traverse1.xlsx",index=False)

print("task complete")