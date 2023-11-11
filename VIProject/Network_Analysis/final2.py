import networkx as nx
import pandas as pd


class DependencyFinder:
    def __init__(self):
        self.Graphtype = nx.Graph()
        self.down_link = list()
        self.dep_nodes = list()
        self.main_graph = list()
        self.sub_graph_list = list()
        self.no_of_gne = list()
        self.nw_type = list()
        self.c = 0
        self.gr_no = list()

    def update_source_target(self, row):
        if row['so_nssid'] in nssid_info['NSSID'].tolist():
            row['source'] += '_GNE'
        if row['si_nssid'] in nssid_info['NSSID'].tolist():
            row['target'] += '_GNE'
        return row

    def nssid_data_formatter(self, path):
        nssid_info = pd.read_excel(path, usecols=['NSSID'])
        nssid_info.dropna(inplace=True)
        nssid_info['NSSID'] = nssid_info['NSSID'].apply(lambda x: x.strip())
        return nssid_info

    def link_data_formatter(self, path):
        links = pd.read_excel(path, usecols=['NEAlias', 'FarEndNEName'])
        links.dropna(inplace=True)
        links.rename({'NEAlias': 'source', 'FarEndNEName': 'target'}, axis=1, inplace=True)
        links['links'] = links['source'] + '-' + links['target']
        links.drop_duplicates(['links'], keep='first', inplace=True)
        links["so_nssid"] = links.source.str.split('_|-', n=1, expand=True)[0]
        links["si_nssid"] = links.target.str.split('_|-', n=1, expand=True)[0]
        links = links.apply(update_source_target, axis=1)
        return links

    def graph_creater(self, df):
        G = nx.from_pandas_edgelist(df, create_using=self.Graphtype)
        dt = pd.DataFrame([])
        dt = pd.concat([df["source"], df["target"]], axis=0, ignore_index=True)
        dt = dt.drop_duplicates()
        node_names = dt.to_list()
        G.add_nodes_from(node_names)
        sub_graphs = nx.connected_components(G)
        return sub_graphs
