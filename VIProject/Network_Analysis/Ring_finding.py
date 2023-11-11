import networkx as nx


def find_rings(graph):
    rings = []
    visited = set()

    def dfs(node, ring):
        if node in visited:
            return
        visited.add(node)
        ring.append(node)

        for neighbor in graph.neighbors(node):
            if neighbor in ring:
                rings.append(ring[ring.index(neighbor):])
            else:
                dfs(neighbor, ring.copy())

    for node in graph.nodes():
        if node not in visited:
            dfs(node, [])

    return rings


def common_nodes_in_same_or_neighboring_ring(graph, gne1, gne2):
    rings = find_rings(graph)

    common_nodes = []

    for ring in rings:
        if gne1 in ring and gne2 in ring:
            common_nodes.extend(ring)

    common_nodes = list(set(common_nodes))  # Remove duplicates

    return common_nodes


# Create a sample graph
G = nx.Graph()
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 5), (5, 1), (5, 6), (6, 7), (7, 8), (8, 9), (9, 6)])

gne1 = 1
gne2 = 7

common_nodes = common_nodes_in_same_or_neighboring_ring(G, gne1, gne2)

print(f"Common nodes in same or neighboring ring with GNEs {gne1} and {gne2}: {common_nodes}")
