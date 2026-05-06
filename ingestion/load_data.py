import pandas as pd
from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# ---------------------------
# LOAD USERS
# ---------------------------
users = pd.read_csv("users.csv")

for _, row in users.iterrows():
    cursor.execute("""
        INSERT INTO users (user_id, country)
        VALUES (%s, %s)
    """, (row["user_id"], row["country"]))

# ---------------------------
# LOAD PRODUCTS
# ---------------------------
products = pd.read_csv("products.csv")

for _, row in products.iterrows():
    cursor.execute("""
        INSERT INTO products (product_id, price)
        VALUES (%s, %s)
    """, (row["product_id"], row["price"]))

# ---------------------------
# LOAD EVENTS
# ---------------------------
events = pd.read_csv("events.csv")

for _, row in events.iterrows():
    cursor.execute("""
        INSERT INTO events (user_id, product_id, event_type, event_timestamp)
        VALUES (%s, %s, %s, %s)
    """, (
        row["user_id"],
        row["product_id"],
        row["event_type"],
        row["event_timestamp"]
    ))

conn.commit()
cursor.close()
conn.close()

print("✅ Data loaded into PostgreSQL")