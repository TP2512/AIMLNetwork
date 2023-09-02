import networkx as nx
import random
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import pandas as pd

linked_list_df = pd.read_excel(r"C:\Users\tpujari\Desktop\infrastructuresvg\VIProject\Network_Analysis\Data\ll_test_single_net.xlsx",usecols=['source', 'target'])
linked_list_df.dropna(inplace=True)
linked_list_df['links'] = linked_list_df['source'] + '-' + linked_list_df['target']
linked_list_df.drop_duplicates(['links'], keep='first', inplace=True)
# Create a graph
Graphtype = nx.Graph()
G = nx.from_pandas_edgelist(linked_list_df, create_using=Graphtype)

# Create a sample graph
# G = nx.erdos_renyi_graph(50, 0.2)  # Random graph with 50 nodes and edge probability 0.2

# Simulate edge breaks and isolated nodes
isolated_nodes = [random.choice(list(G.nodes)) for _ in range(5)]
print(isolated_nodes)
for node in isolated_nodes:
    neighbors = list(G.neighbors(node))
    if neighbors:
        edge_to_break = random.choice(neighbors)
        G.remove_edge(node, edge_to_break)

# Generate features and labels for nodes
features = []
labels = []
for node in G.nodes:
    neighbors = list(G.neighbors(node))
    features.append([len(neighbors), nx.degree_centrality(G)[node], nx.betweenness_centrality(G)[node]])
    labels.append(node in isolated_nodes)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

# Train Random Forest classifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)
print(X_test,y_pred)
# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
