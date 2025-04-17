import pandas as pd
df = pd.read_csv('supermarket_sales.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.to_period('M')
chunks = [
    f"Product: {row['Product line']}, Sales: {row['Total']}, City: {row['City']}, Date: {row['Date']}"
    for _, row in df.iterrows()
]
