from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go

# --------------------------------------------
# Data Scraping (same as before)
# --------------------------------------------
def scrape_walmart(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    product_names = [item.get_text() for item in soup.select('span.product-title')]
    prices = [price.get_text() for price in soup.select('span.price')]

    walmart_data = pd.DataFrame({
        'Product': product_names,
        'Price': prices
    })
    return walmart_data






# Load CSVs for further processing
walmart_data = pd.read_csv("D:\study\datamining\project\new.csv")
food_basics_data = pd.read_csv("D:\study\datamining\project\foodbasics_products.csv")

# --------------------------------------------
# Data Preprocessing (same as before)
# --------------------------------------------
def preprocess_data(data):
    data['Price'] = data['Price'].str.replace('$', '').astype(float)  # Remove dollar signs
    data.drop_duplicates(inplace=True)
    data.dropna(inplace=True)
    data['Product'] = data['Product'].str.lower()  # Normalize product names
    return data

# Preprocess Walmart and Food Basics data
walmart_cleaned = preprocess_data(walmart_data)
food_basics_cleaned = preprocess_data(food_basics_data)

# Combine datasets for analysis
combined_data = pd.concat([walmart_cleaned, food_basics_cleaned])
print(combined_data.head())

# --------------------------------------------
# Market Basket Analysis (same as before)
# --------------------------------------------
# Example transaction data
data = {'Transaction': [1, 1, 1, 2, 2, 3],
        'Product': ['apple', 'banana', 'milk', 'apple', 'milk', 'banana']}

basket_df = pd.DataFrame(data)

# Pivot data to create a basket matrix (one-hot encoding)
basket = pd.pivot_table(basket_df, index='Transaction', columns='Product', aggfunc=len, fill_value=0)

# Apply Apriori to get frequent itemsets
frequent_itemsets = apriori(basket, min_support=0.5, use_colnames=True)

# Generate association rules
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
print(rules)

# --------------------------------------------
# Visualization of Association Rules using Plotly
# --------------------------------------------
# Prepare data for Plotly network graph
edge_list = []
for i, row in rules.iterrows():
    for antecedent in row['antecedents']:
        for consequent in row['consequents']:
            edge_list.append((antecedent, consequent, row['confidence']))

# Create a list of nodes and edges for the network
nodes = list(set([n for edge in edge_list for n in edge[:2]]))
edges = [{'from': edge[0], 'to': edge[1], 'confidence': edge[2]} for edge in edge_list]

# Create the node positions in a circular layout
positions = {node: (i, 1) for i, node in enumerate(nodes)}

# Build the figure using Plotly
edge_trace = go.Scatter(
    x=[],
    y=[], 
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

for edge in edges:
    x0, y0 = positions[edge['from']]
    x1, y1 = positions[edge['to']]
    edge_trace['x'] += [x0, x1, None]
    edge_trace['y'] += [y0, y1, None]

node_trace = go.Scatter(
    x=[], y=[], 
    text=[], 
    mode='markers+text', 
    hoverinfo='text', 
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Confidence',
            xanchor='left',
            titleside='right')
    )
)

for node in nodes:
    x, y = positions[node]
    node_trace['x'] += [x]
    node_trace['y'] += [y]
    node_trace['text'] += [node]

# Create and show Plotly figure
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Association Rule Network',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0,l=0,r=0,t=40),
                    xaxis=dict(showgrid=False, zeroline=False),
                    yaxis=dict(showgrid=False, zeroline=False))
                )

fig.show()

# --------------------------------------------
# Machine Learning: Prediction Model (same as before)
# --------------------------------------------
# Predict if 'milk' is bought based on other products
X = basket.drop('milk', axis=1)  # Features (other products)
y = basket['milk']  # Label (if milk is bought)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)

# --------------------------------------------
# Model Accuracy Evaluation (same as before)
# --------------------------------------------
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

# Display results
print(f'Accuracy: {accuracy}')
print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F1-Score: {f1}')

# Cross-validated accuracy
cv_scores = cross_val_score(clf, X, y, cv=5, scoring='accuracy')
print(f'Cross-validated Accuracy: {cv_scores.mean()}')
