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

nssid_info = pd.read_excel(r"Data\UPE\nssid.xlsx",usecols=['NSSID'])
nssid_info.dropna(inplace=True)
nssid_info['NSSID'] = nssid_info['NSSID'].apply(lambda x: x.strip())

links = pd.read_excel(r"Data\UPE\link_list.xlsx",usecols=['NEAlias', 'FarEndNEName'])
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
        subgraph_edges = subgraph.edges()
        try:
            nx.find_cycle(subgraph)
            #------------------------something wrong plz check----------------------------------------
            cycles = list(nx.cycle_basis(new_graph_gne))
            all_edges = set(new_graph_gne.edges())
            edges_in_cycles=set()
            edges_in_cycles_for_search = set()
            for cycle in cycles:
                for i in range(len(cycle)):
                    edges_in_cycles_for_search.add((cycle[i], cycle[(i + 1) % len(cycle)]))
                    edges_in_cycles.add((cycle[i], cycle[(i + 1) % len(cycle)]))
                    edges_in_cycles_for_search.add((cycle[(i + 1) % len(cycle)],cycle[i]))
            edges_not_in_cycles = all_edges - edges_in_cycles_for_search
            if len(edges_not_in_cycles)>=1:
                nw_type_str="Mesh"
            else:
                nw_type_str="Ring"
            combinations = list(itertools.combinations(edges_in_cycles, 2))
            #combinations.extend(edges_not_in_cycles)
            #------------------------------------------------------------------
            for combo in combinations:
                name_of_gne.append(ng)
                main_nw_graph_type.append(main_nw_graph_type_str)
                nw_type.append(nw_type_str)
                # print("combo",combo)
                main_graph.append(sg1)
                sub_graph_list.append(sg)
                no_of_gne.append(no_gnes)
                down_link.append(combo)
                time.sleep(0.001)
                #print("ring length of downlink", len(down_link))
                gr_no.append(c)
                for edge_to_remove in combo:
                    new_graph_gne.remove_edge(*edge_to_remove)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                node_list=[]
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        node_list.extend(i)
                dep_nodes.append(node_list)
                #print(" ring length of dep nodes", len(dep_nodes))
                # print("node_list",node_list)
                for edge_to_add in combo:
                    new_graph_gne.add_edge(*edge_to_add)
            for combo in edges_not_in_cycles:
                name_of_gne.append(ng)
                main_nw_graph_type.append(main_nw_graph_type_str)
                nw_type.append(nw_type_str)
                # print("combo",combo)
                main_graph.append(sg1)
                sub_graph_list.append(sg)
                no_of_gne.append(no_gnes)
                down_link.append(combo)
                print("ring-spur length of downlink", len(down_link))
                gr_no.append(c)
                new_graph_gne.remove_edge(*combo)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                node_list=[]
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        node_list.extend(i)
                dep_nodes.append(node_list)
                #print(" ring length of dep nodes", len(dep_nodes))
                # print("node_list",node_list)
                new_graph_gne.add_edge(*combo)
        except nx.exception.NetworkXNoCycle:
            for edge in new_graph_gne.edges:
                # print("subgraph_edges",edge)
                name_of_gne.append(ng)
                main_graph.append(sg1)
                main_nw_graph_type.append(main_nw_graph_type_str)
                down_link.append(edge)
                print("spur length of downlink", len(down_link))
                nw_type.append("Spur")
                sub_graph_list.append(sg)
                no_of_gne.append(no_gnes)
                gr_no.append(c)
                new_graph_gne.remove_edge(*edge)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                node_list = []
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        node_list.extend(i)
                dep_nodes.append(node_list)
                #print(" spur length of dep nodes", len(dep_nodes))
                new_graph_gne.add_edge(*edge)

list_of_edges=pd.DataFrame()
list_of_edges.insert(0, "Network Type(Main Network)", main_nw_graph_type)
list_of_edges.insert(1, "Main Network Group", main_graph)
list_of_edges.insert(2, "Main Network Group ID", gr_no)
list_of_edges.insert(3, "Sub Network Type", nw_type)
list_of_edges.insert(4, "SubNetwork", sub_graph_list)
list_of_edges.insert(5, "No of GNE", no_of_gne)
list_of_edges.insert(6, "Name of GNE", name_of_gne)
list_of_edges.insert(7, "Dependent Link", down_link)
list_of_edges.insert(8, "dep_nodes", dep_nodes)
list_of_edges.to_excel("network_paths.xlsx",index=False)
print("task complete")