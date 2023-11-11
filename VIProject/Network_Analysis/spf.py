import networkx as nx
import pandas as pd


# Read the Excel file and create a graph
def create_graph_from_excel(excel_file):
    G = nx.Graph()
    df = pd.read_excel(excel_file)
    for index, row in df.iterrows():
        source, sink = row['source'], row['target']
        G.add_edge(source, sink)
    return G


# Find the shortest path between source and sink nodes
def find_shortest_path(graph, source, sink):
    try:
        shortest_path = nx.shortest_path(graph, source=source, target=sink)
        return shortest_path
    except nx.NetworkXNoPath:
        return None  # No path exists


# Provide your Excel file
excel_file = r"Data\ll_test_single_net.xlsx"
source_node = 'source'
sink_node = 'target'

# Create the graph
graph = create_graph_from_excel(excel_file)

# Find the shortest path
shortest_path = find_shortest_path(graph, source_node, sink_node)

if shortest_path:
    print(f"Shortest path between {source_node} and {sink_node}: {shortest_path}")
else:
    print(f"No path found between {source_node} and {sink_node}.")
