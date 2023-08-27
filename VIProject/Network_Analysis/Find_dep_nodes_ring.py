import networkx as nx
import pandas as pd
import itertools

def get_farthest_node(G,source: str,edge_to_remove: tuple) -> str:
    shortest_path_length_a_b = nx.shortest_path_length(G, source=gne_node, target=edge_to_remove[0])
    shortest_path_length_a_c = nx.shortest_path_length(G, source=gne_node, target=edge_to_remove[1])
    if shortest_path_length_a_b > shortest_path_length_a_c:
        start_node = edge_to_remove[0]
    else:
        start_node = edge_to_remove[1]
    return start_node

linked_list_df = pd.read_excel(r"Data\ll_test_single_net.xlsx",usecols=['source', 'target'])
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)
# Create a graph
Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)
sub_graphs = nx.connected_components(G)

for i, sg in enumerate(sub_graphs):
    print('main graphs',sg)
    gne_llst = [j for j in sg if "_GNE" in j]
    gne_node = gne_llst[0]
    subgraph = G.subgraph(sg)
    subgraph_edges = subgraph.edges()
    print(subgraph_edges)

    try:
        nx.find_cycle(subgraph)
        cycle_list = nx.cycle_basis(G)
        print("cycle list",cycle_list)
        #cycle_edges = list()
        #for cycle in cycle_list:
        #    cycle_edges.update(zip(cycle, cycle[1:] + [cycle[0]]))
        #print(cycle_edges,"cycle_edges")
        #list_of_nodes_in_cycle=list(nx.find_cycle(subgraph))
        combinations = list(itertools.combinations(subgraph_edges, 2))
        print(combinations)
        for combo in combinations:
            all_ele_combo=combo[0]+combo[1]
            print("all_ele_combo",all_ele_combo)
            if all(element in cycle_list[0] for element in all_ele_combo):
                print(combo)
                edge_to_remove=combo[0]
                G.remove_edge(*edge_to_remove)
                start_node = get_farthest_node(G, gne_node, edge_to_remove)

                edge_to_remove = combo[1]
                G.remove_edge(*edge_to_remove)
                dfs_tree = nx.dfs_tree(G, source=start_node)
                print("\nDependent Nodes:")
                print(dfs_tree.nodes(), "\n")
                edge_to_add = combo[0]
                G.add_edge(*edge_to_add)
                edge_to_add = combo[1]
                G.add_edge(*edge_to_add)
    except :
        for edge in subgraph_edges:
            edge_to_remove = edge
            print(edge)
            start_node = get_farthest_node(G, gne_node, edge_to_remove)
            G.remove_edge(*edge_to_remove)
            dfs_tree = nx.dfs_tree(G, source=start_node)
            print("\nDependent Nodes:")
            print(dfs_tree.nodes(), "\n")
            G.add_edge(*edge)
