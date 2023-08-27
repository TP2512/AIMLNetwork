import networkx as nx

import pandas as pd
import itertools

linked_list_df = pd.read_excel(r"C:\Users\tpujari\Desktop\infrastructuresvg\VIProject\Network_Analysis\Data\ll_test_multigne_net.xlsx",usecols=['source', 'target'])
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)
# Create a graph
Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)
# Find "GNE" nodes
gne_nodes = [node for node in G.nodes if "GNE" in node]
#print("gne_nodes",gne_nodes)
# Group nodes based on proximity to "GNE" nodes
node_groups = {gne_node: set([gne_node]) for gne_node in gne_nodes}
#print("node_groups",node_groups)
#print("nodes in network",G.nodes)
for node in G.nodes:
    if "GNE" not in node:
        #print("Searched_Node",node)
        shortest_distances = {
            gne_node: nx.shortest_path_length(G, node, gne_node) for gne_node in gne_nodes
        }
        #print("shortest_distances",shortest_distances)
        min_distance = min(shortest_distances.values())

        # Find all "GNE" nodes with the same minimum distance
        closest_gne_nodes = [gne_node for gne_node, distance in shortest_distances.items() if distance == min_distance]
        #print("closest_gne_nodes",closest_gne_nodes)
        # Add the node to each corresponding group
        for gne_node in closest_gne_nodes:
            node_groups[gne_node].add(node)
        #print("node_groups",node_groups)

print("Node groups:")
for gne_node, group in node_groups.items():
    print(f"Nodes close to {gne_node}: {group}")
