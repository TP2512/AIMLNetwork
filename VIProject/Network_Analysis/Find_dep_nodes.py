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

edge_to_remove=('a15','a13')
gne_node='a10_GNE'

start_node=get_farthest_node(G,gne_node,edge_to_remove)
G.remove_edge(*edge_to_remove)
dfs_tree = nx.dfs_tree(G, source=start_node)

print("\nDependent Nodes:")
print(dfs_tree.nodes())

# # Perform DFS traversal to find dependent nodes
# def dfs(graph, node, visited):
#     visited.append(node)
#     for neighbor in graph.neighbors(node):
#         if neighbor not in visited:
#             dfs(graph, neighbor, visited)
#
# visited = list()
# node='a10_GNE'
# dfs(G, node,  visited)
# print("from GNE",visited)
#
# edge_to_remove=('a12','a11')
# G.remove_edge(*edge_to_remove)
# #edge_to_remove=('a5','a4')
# #G.remove_edge(*edge_to_remove)
# node1=visited.index(edge_to_remove[0])
# print("node1",node1)
# node2=visited.index(edge_to_remove[1])
# print("node1",node2)
# leftest_ele_ind=max(node1,node2)
# dependent_nodes_list = list()
# dfs(G, visited[leftest_ele_ind],  dependent_nodes_list)
# print("from removed edge")
# print("dependent nodes",dependent_nodes_list)
#
