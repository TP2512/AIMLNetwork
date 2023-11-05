import networkx as nx
import pandas as pd

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 4), (2, 4) , (4,5)])
source_node = 1
all_paths = []
gne_list=[]
link_list=[]
path_list=[]
summarylist=[]
for edge in G.edges():
    G.remove_edge(*edge)
    path_len = []
    if source_node in edge:
        print(edge,source_node,edge)
        path_len.append(0)
        link_list.append(edge)
        gne_list.append(source_node)
        path_list.append(edge)
    for target_node in edge:
        paths = list(nx.all_simple_edge_paths(G, source=source_node, target=target_node))
        for path in paths:
            path_len.append(len(path))
            link_list.append(edge)
            gne_list.append(source_node)
            path_list.append(path)
            print(edge,source_node,path)
    link_list.append(edge)
    gne_list.append("summary")
    path_list.append(path_len)
    print(f"summary-{edge} {sorted(path_len)}")
    G.add_edge(*edge)
# for target_node in G.nodes():
#     if source_node != target_node:
#         paths = list(nx.all_simple_edge_paths(G, source=source_node, target=target_node))
#         for path in paths:
#             for link in path:
#                 if target_node in link:
#                     print("gne",source_node,"target",target_node,"link",link,"path",path)
#                     gne_list.append(source_node)
#                     target_list.append(target_node)
#                     link_list.append(link)
#                     path_list.append(path)

list_of_edges=pd.DataFrame()
list_of_edges.insert(0, "GNE", gne_list)
list_of_edges.insert(1, "Link", link_list)
list_of_edges.insert(2, "Path", path_list)
list_of_edges.to_excel("network_traverse1.xlsx",index=False)
print("task complete")

