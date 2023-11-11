import itertools

import networkx as nx
import pandas as pd


def update_source_target(row):
    if row['so_nssid'] in nssid_info['NSSID'].tolist():
        row['source'] += '_GNE'
    if row['si_nssid'] in nssid_info['NSSID'].tolist():
        row['target'] += '_GNE'
    return row


nssid_info = pd.read_excel(r"Data\nssid.xlsx", usecols=['NSSID'])
nssid_info.dropna(inplace=True)
nssid_info['NSSID'] = nssid_info['NSSID'].apply(lambda x: x.strip())

links = pd.read_excel(r"Data\link_list_odi.xlsx", usecols=['NEAlias', 'FarEndNEName'])
links.dropna(inplace=True)
links.rename({'NEAlias': 'source', 'FarEndNEName': 'target'}, axis=1, inplace=True)
links['links'] = links['source'] + '-' + links['target']
links.drop_duplicates(['links'], keep='first', inplace=True)
links["so_nssid"] = links.source.str.split('_|-', n=1, expand=True)[0]
links["si_nssid"] = links.target.str.split('_|-', n=1, expand=True)[0]
links = links.apply(update_source_target, axis=1)
links.to_excel("links.xlsx")

dt = pd.DataFrame([])
dt = pd.concat([links["source"], links["target"]], axis=0, ignore_index=True)
dt = dt.drop_duplicates()
node_names = dt.to_list()

# 2.mesh data with spur structure also containing multiple links

Graphtype = nx.Graph()

G = nx.from_pandas_edgelist(links, create_using=Graphtype)
G.add_nodes_from(node_names)
sub_graphs = nx.connected_components(G)

main_nw_graph_type = []
down_link = []
dep_nodes = []
main_graph = []
sub_graph_list = []
no_of_gne = []
nw_type = []
c = 0
gr_no = []

for i, sg1 in enumerate(sub_graphs):
    subgraph = G.subgraph(sg1)
    c += 1
    new_graph = subgraph.copy()
    try:
        nx.find_cycle(subgraph)
        main_nw_graph_type_str = "Mesh"
    except:
        main_nw_graph_type_str = "Spur"
    gne_nodes = [node for node in new_graph.nodes if "GNE" in node]
    no_gnes = len(gne_nodes)
    node_groups = {gne_node: set([gne_node]) for gne_node in gne_nodes}
    for node in new_graph.nodes:
        if "GNE" not in node:
            shortest_distances = {
                gne_node: nx.shortest_path_length(new_graph, node, gne_node) for gne_node in gne_nodes
            }
            try:
                min_distance = min(shortest_distances.values())
            except ValueError:
                min_distance = 0
            closest_gne_nodes = [gne_node for gne_node, distance in shortest_distances.items() if
                                 distance == min_distance]
            for gne_node in closest_gne_nodes:
                node_groups[gne_node].add(node)

    for ng, sg in node_groups.items():
        # print("GNE node,sg",ng,sg)
        subgraph = G.subgraph(sg)
        gne_llst = [j for j in sg if "_GNE" in j]
        gne_node = gne_llst[0]
        new_graph_gne = subgraph.copy()
        subgraph_edges = subgraph.edges()
        try:
            nx.find_cycle(subgraph)
            # print("Have Ring")
            combinations = list(itertools.combinations(subgraph_edges, 2))
            for combo in combinations:
                main_nw_graph_type.append(main_nw_graph_type_str)
                nw_type.append("Ring")
                main_graph.append(sg1)
                sub_graph_list.append(sg)
                no_of_gne.append(no_gnes)
                down_link.append(combo)
                gr_no.append(c)
                for edge_to_remove in combo:
                    new_graph_gne.remove_edge(*edge_to_remove)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                # print("Dependent Nodes: ", end="")
                node_list = []
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        node_list.append(i)
                dep_nodes.append(node_list)
                for edge_to_add in combo:
                    new_graph_gne.add_edge(*edge_to_add)
            # print("\n")
        except:
            # print("Dont have Rings")
            for edge in subgraph_edges:
                main_graph.append(sg1)
                down_link.append(edge)
                main_nw_graph_type.append(main_nw_graph_type_str)
                nw_type.append("Spur")
                sub_graph_list.append(sg)
                no_of_gne.append(no_gnes)
                gr_no.append(c)
                new_graph_gne.remove_edge(*edge)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                # print("Dependent Nodes: ", end="")
                node_list = []
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        node_list.append(i)
                dep_nodes.append(node_list)
                new_graph_gne.add_edge(*edge)

list_of_edges = pd.DataFrame()

list_of_edges.insert(0, "Network Type(Main Network)", main_nw_graph_type)
list_of_edges.insert(1, "Main Network Group", main_graph)
list_of_edges.insert(2, "group no", gr_no)
list_of_edges.insert(3, "Sub Network Type", nw_type)
list_of_edges.insert(4, "SubNetwork", sub_graph_list)
list_of_edges.insert(5, "No of GNE", no_of_gne)
list_of_edges.insert(6, "down_link", down_link)
list_of_edges.insert(7, "dep_nodes", dep_nodes)
list_of_edges.to_excel("network_paths.xlsx", index=False)
print("task complete")
