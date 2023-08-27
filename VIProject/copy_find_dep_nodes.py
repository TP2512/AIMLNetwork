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
    gne_llst = [j for j in sg if "_GNE" in j]
    gne_node = gne_llst[0]
    subgraph = G.subgraph(sg)
    new_graph = subgraph.copy()
    subgraph_edges = subgraph.edges()
    try:
        nx.find_cycle(subgraph)
        combinations = list(itertools.combinations(subgraph_edges, 2))
        for combo in combinations:
            print("\nLinks Down:",combo)
            for edge_to_remove in combo:
                new_graph.remove_edge(*edge_to_remove)
            sub_graphs_new_gr = nx.connected_components(new_graph)
            print("Dependent Nodes: ",end="")
            for i in sub_graphs_new_gr:
                if gne_node not in i:
                    print(i,end="")
            for edge_to_add in combo:
                new_graph.add_edge(*edge_to_add)
        print("\n")
    except :
        for edge in subgraph_edges:
            print("\nLink Down:",edge)
            new_graph.remove_edge(*edge)
            sub_graphs_new_gr = nx.connected_components(new_graph)
            print("Dependent Nodes: ",end="")
            for i in sub_graphs_new_gr:
                if gne_node not in i:
                    print(i,end="")
            new_graph.add_edge(*edge)
