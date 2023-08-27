import networkx as nx
import pandas as pd
import itertools

linked_list_df = pd.read_excel(r"C:\Users\tpujari\Desktop\infrastructuresvg\VIProject\Network_Analysis\Data\ll_test_single_net.xlsx",usecols=['source', 'target'])
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)
# Create a graph
Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)
sub_graphs = nx.connected_components(G)

for i, sg in enumerate(sub_graphs):
    print('main graphs',sg)
    subgraph = G.subgraph(sg)
    new_graph = subgraph.copy()
    gne_nodes = [node for node in new_graph.nodes if "GNE" in node]
    node_groups = {gne_node: set([gne_node]) for gne_node in gne_nodes}
    for node in new_graph.nodes:
        if "GNE" not in node:
            shortest_distances = {
                gne_node: nx.shortest_path_length(new_graph, node, gne_node) for gne_node in gne_nodes
            }
            min_distance = min(shortest_distances.values())
            closest_gne_nodes = [gne_node for gne_node, distance in shortest_distances.items() if
                                 distance == min_distance]
            for gne_node in closest_gne_nodes:
                node_groups[gne_node].add(node)

    for ng,sg in node_groups.items():
        print("ng,sg",ng,sg)
        subgraph = G.subgraph(sg)
        gne_llst = [j for j in sg if "_GNE" in j]
        gne_node = gne_llst[0]
        new_graph_gne = subgraph.copy()
        subgraph_edges = subgraph.edges()
        try:
            nx.find_cycle(subgraph)
            print("Have Ring")
            combinations = list(itertools.combinations(subgraph_edges, 2))
            for combo in combinations:
                print("\nLinks Down:", combo)
                for edge_to_remove in combo:
                    new_graph_gne.remove_edge(*edge_to_remove)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                print("Dependent Nodes: ", end="")
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        print(i, end="")
                for edge_to_add in combo:
                    new_graph_gne.add_edge(*edge_to_add)
            print("\n")
        except:
            print("Dont have Rings")
            for edge in subgraph_edges:
                print("\nLink Down:", edge)
                new_graph_gne.remove_edge(*edge)
                sub_graphs_new_gr = nx.connected_components(new_graph_gne)
                print("Dependent Nodes: ", end="")
                for i in sub_graphs_new_gr:
                    if gne_node not in i:
                        print(i, end="")
                new_graph_gne.add_edge(*edge)
