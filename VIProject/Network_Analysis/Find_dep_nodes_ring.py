import networkx as nx
import pandas as pd

# Create a graph
linked_list_df = pd.read_excel(r"Data\ll_test_single_net.xlsx",usecols=['source', 'target'])
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)

Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)

def get_farthest_node(G: Graphtype,source: str,edge_to_remove: tuple) -> str:
    shortest_path_length_a_b = nx.shortest_path_length(G, source=gne_node, target=edge_to_remove[0])
    shortest_path_length_a_c = nx.shortest_path_length(G, source=gne_node, target=edge_to_remove[1])
    if shortest_path_length_a_b > shortest_path_length_a_c:
        start_node = edge_to_remove[0]
    else:
        start_node = edge_to_remove[1]
    return start_node

gne_node='a1_GNE'
edge_to_remove=('a1_GNE','a5')
G.remove_edge(*edge_to_remove)
edge_to_remove=('a2','a1_GNE')
start_node=get_farthest_node(G,gne_node,edge_to_remove)
G.remove_edge(*edge_to_remove)

dfs_tree = nx.dfs_tree(G, source=start_node)

print("\nDependent Nodes:")
print(dfs_tree.nodes())
