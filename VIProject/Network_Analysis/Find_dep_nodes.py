import networkx as nx
import pandas as pd

# Create a graph
linked_list_df = pd.read_excel(r"Data\ll_test_single_net.xlsx",usecols=['source', 'target'])
no_of_rows=linked_list_df.shape[0] #get number of rows
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)

Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)

# Perform DFS traversal to find dependent nodes
def dfs(graph, node, visited):
    visited.append(node)
    for neighbor in graph.neighbors(node):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

visited = list()
node='a10_GNE'
dfs(G, node,  visited)
print("from GNE",visited)

edge_to_remove=('a12','a11')
G.remove_edge(*edge_to_remove)
#edge_to_remove=('a5','a4')
#G.remove_edge(*edge_to_remove)
node1=visited.index(edge_to_remove[0])
print("node1",node1)
node2=visited.index(edge_to_remove[1])
print("node1",node2)
leftest_ele_ind=max(node1,node2)
dependent_nodes_list = list()
dfs(G, visited[leftest_ele_ind],  dependent_nodes_list)
print("from removed edge")
print("dependent nodes",dependent_nodes_list)


