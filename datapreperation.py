import pandas as pd
import random

# Load datasets
df1 = pd.read_csv('/')
df2 = pd.read_csv('/content/walmart_products.csv')

# werging the datasets based on 'Title'
merged_df = pd.merge(df1, df2, on='Title', how='outer')

# Cleaning  data
merged_df = merged_df.dropna(subset=['Title'])  # Drop rows without product titles
merged_df = merged_df.drop_duplicates(subset=['Title'])  # Remove duplicate products

# Clean price columns (removing  dollar signs and convert to float)
merged_df['Price_x'] = merged_df['Price_x'].replace({'\$': ''}, regex=True).astype(float, errors='ignore')
merged_df['Price_y'] = merged_df['Price_y'].replace({'\$': ''}, regex=True).astype(float, errors='ignore')

# Merge 'Price_x' and 'Price_y' into one 'Price' column
merged_df['Price'] = merged_df['Price_x'].combine_first(merged_df['Price_y'])
merged_df = merged_df.drop(columns=['Price_x', 'Price_y'])  # Drop the original price columns

# Prepare data for market basket analysis
# Simulating transactions - assume we randomly assign products to transactions for analysis
num_transactions = 100  # Example: 100 transactions
products_list = list(merged_df['Title'])  # List of available products

# Randomly assign products to transactions
transaction_data = []

for i in range(num_transactions):
    # Randomly pick products for each transaction (between 1 and 10 products per transaction)
    num_products_in_transaction = random.randint(1, 10)
    products_in_transaction = random.sample(products_list, num_products_in_transaction)
    transaction_data.append([f'Transaction_{i+1}'] + products_in_transaction)

# Convert to DataFrame: First column will be Transaction ID, others will be product titles
transaction_df = pd.DataFrame(transaction_data)

# Convert the transaction dataframe into a binary format (market basket format)
# First, we explode the dataframe so that each product in a transaction is in a separate row
transactions_exploded = transaction_df.melt(id_vars=[0], value_name='Product').dropna(subset=['Product'])

# Create one-hot encoding using pivot table
basket_df = pd.pivot_table(transactions_exploded, index=0, columns='Product', aggfunc='size', fill_value=0)

# Output the result
print(basket_df.head())

# Save the result for future use
basket_df.to_csv('market_basket_analysis_data.csv', index=False)
