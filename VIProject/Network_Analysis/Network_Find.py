import os

import networkx as nx
import pandas as pd
from pyvis.network import Network


def node_list_to_edge_list(a):
    edge_list = []
    attrs = {}
    counter = 0
    while counter < len(a) - 1:
        source = a[counter]
        target = a[counter + 1]
        lis = [source, target]
        tup = tuple(lis)
        edge_list.append(tup)
        counter += 1
    return edge_list


def plot_graph_final(s, gr):
    os.chdir("GRAPHS")
    plt_g = nx.Graph()
    plt_g.add_nodes_from(set([element for innerList in gr for element in innerList]))
    plt_g.add_node(gr[0][0], title='GNE', color='#00ff1e', size=14)
    # plt_g.add_node(gr[-1], title='Sink',color='#dd4b39',size=14)
    for i in gr:
        # print(i)
        edge_list = []
        counter = 0
        while counter < len(i) - 1:
            source = i[counter]
            target = i[counter + 1]
            lis = [source, target]
            tup = tuple(lis)
            edge_list.append(tup)
            counter += 1
            # print(edge_list)
            plt_g.add_edges_from(edge_list)

    # plt_g.add_edges_from(edge_list)
    # nx.draw(plt_g, with_labels=True)
    # fig_name1=s+'.svg'
    # plt.savefig(fig_name1,with_labels = True)
    # plt.savefig(fig_name1, optimize=True, progressive=True)
    # plt.clf()
    nt = Network('600px', '1000px', notebook=False)
    nt.from_nx(plt_g)
    fig_name = s + '.html'
    # nt.save_graph(fig_name)
    nt.write_html(fig_name)
    os.chdir("..")
    os.system("taskkill /im iexplore.exe /f")


eci_node_info = pd.read_excel(r"C:\Users\22002626\Downloads\TARKESH-TREE STRUCTURE\GUJ\eci ne list.xlsx",
                              usecols=['NodeName', 'NSSID'])
eci_node_info.dropna(inplace=True)
eci_node_info = eci_node_info[~eci_node_info.NodeName.str.contains("_EBG20|_EUXD", case=False)]
eci_node_info['NSSID'] = eci_node_info['NSSID'].apply(lambda x: x.strip())

huawei_node_info = pd.read_excel(r"C:\Users\22002626\Downloads\TARKESH-TREE STRUCTURE\GUJ\huawei ne list.xlsx",
                                 usecols=['NE Name', 'NE Subtype', 'Remarks'])
huawei_node_info = huawei_node_info[huawei_node_info['NE Subtype'].str.contains("OptiX")]
huawei_node_info = huawei_node_info[['NE Name', 'Remarks']]
huawei_node_info.rename({'NE Name': 'NodeName', 'Remarks': 'NSSID'}, axis=1, inplace=True)

nssid_df = pd.concat([eci_node_info, huawei_node_info])
nssid_df.dropna(inplace=True)

links = pd.read_excel(
    r"C:\Users\22002626\Downloads\TARKESH-TREE STRUCTURE\GUJ\SOMDSPGJ_Config_Data_MINI-LINK_TN_MMU2B_C_20230202_074831.xlsx")
links = links[['NEAlias', 'FarEndNEName']]
links.dropna(inplace=True)
links.rename({'NEAlias': 'source', 'FarEndNEName': 'target'}, axis=1, inplace=True)
links['links'] = links['source'] + '-' + links['target']
links.drop_duplicates(['links'], inplace=True)
links["so_nssid"] = links.source.str.split('-', n=1, expand=True)[0]
links["si_nssid"] = links.target.str.split('-', n=1, expand=True)[0]
# links['link']=links['so_nssid']+'-'+links['si_nssid']
# links.drop_duplicates(['link'],inplace=True)
so_mapped = pd.merge(links, nssid_df, left_on='so_nssid', right_on='NSSID', how='inner')
so_mapped['source'] = so_mapped.source + '_GNE'
si_mapped = pd.merge(links, nssid_df, left_on='si_nssid', right_on='NSSID', how='inner')
si_mapped['target'] = si_mapped.target + '_GNE'
con_df = pd.concat([so_mapped, si_mapped])
con_df.drop_duplicates(['links'], inplace=True)
con_df = con_df[['source', 'target', 'links', 'so_nssid', 'si_nssid']]
final = pd.concat([con_df, links])
final.drop_duplicates(['links'], keep='first', inplace=True)
final.to_excel("final.xlsx")
sheet6 = final["source"]
sheet7 = final["target"]
dt = pd.DataFrame([])
dt = pd.concat([sheet6, sheet7], axis=0, ignore_index=True)
dt = dt.drop_duplicates()
node_names = dt.to_list()
Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(final, create_using=Graphtype)
G.add_nodes_from(node_names)
sub_graphs = nx.connected_components(G)
list_of_networks = pd.DataFrame()
list_of_net = []
for i, sg in enumerate(sub_graphs):
    list_of_net.append(sg)

list_of_networks.insert(0, "listofnetwork", list_of_net)
list_of_networks.to_excel("networkx.xlsx")
print("group finding complete")

# list_of_net1=list_of_net.copy()
list_of_edges = pd.DataFrame()
all_paths = []
list_of_grp = []
list_of_gne = []
list_of_sink = []
counter = 0

for i in list_of_net:
    grp_no = "GRP-" + str(counter)
    gne_llst = [j for j in i if "_GNE" in j]
    if gne_llst:
        s = gne_llst[0]
    else:
        s = list(i)[0]
    i.remove(s)
    path_list = []
    for k in i:
        a = list(nx.all_simple_paths(G, s, k))
        for j in a:
            all_paths.append(j)
            list_of_grp.append(grp_no)
            # s=s.replace('_GNE','')
            list_of_gne.append(s)
            list_of_sink.append(k)
            path_list.append(j)
    counter += 1
    # flatList=[]
    # flatList.append(s)
    # flatList = [element for innerList[1:] in path_list for element in innerList]
    # plot_graph_final(s,gr=path_list)

list_of_edges.insert(0, "Group_ID", list_of_grp)
list_of_edges.insert(1, "ListOfEdges", all_paths)
list_of_edges.insert(2, "GNE_Name", list_of_gne)
list_of_edges.insert(3, "Site_Name", list_of_sink)
list_of_edges.to_excel("network_paths.xlsx")

print("task complete")
