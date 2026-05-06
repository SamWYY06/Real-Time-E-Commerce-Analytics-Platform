import pandas as pd
import numpy as np

# ---------------------------
# CONFIG
# ---------------------------
NUM_USERS = 1000
NUM_PRODUCTS = 500
NUM_DATA = 10000

# ---------------------------
# 👤 USERS
# ---------------------------
def generate_users():
    return pd.DataFrame({
        "user_id": np.arange(1, NUM_USERS + 1),
        "country": np.random.choice(["MY", "US", "SG", "UK"], NUM_USERS)
    })

# ---------------------------
# 🛍 PRODUCTS
# ---------------------------
def generate_products():
    return pd.DataFrame({
        "product_id": np.arange(1, NUM_PRODUCTS + 1),
        "price": np.round(np.random.uniform(5, 500, NUM_PRODUCTS), 2)
    })

# ---------------------------
# 📊 DATA
# ---------------------------
def generate_data():
    start_time = pd.to_datetime("2024-01-01")

    return pd.DataFrame({
        "event_id": np.arange(1, NUM_DATA + 1),
        "user_id": np.random.randint(1, NUM_USERS + 1, NUM_DATA),
        "product_id": np.random.randint(1, NUM_PRODUCTS + 1, NUM_DATA),
        "event_type": np.random.choice(["view", "click", "purchase"], NUM_DATA),
        "event_timestamp": start_time + pd.to_timedelta(np.arange(NUM_DATA), unit="s")
    })

# ---------------------------
# 🧨 DATA QUALITY ISSUES (DATA ONLY)
# ---------------------------
def inject_noise(data):
    n = len(data)

    # NULLS
    null_idx = np.random.choice(n, size=int(0.05 * n), replace=False)
    data.loc[null_idx, "user_id"] = np.nan

    # OUTLIERS (simulate weird data points)
    outlier_idx = np.random.choice(n, size=int(0.02 * n), replace=False)
    data.loc[outlier_idx, "event_type"] = "unknown_event"

    # DUPLICATES
    dup = data.sample(frac=0.02)
    data = pd.concat([data, dup], ignore_index=True)

    return data

# ---------------------------
# 💾 SAVE FILES
# ---------------------------
def main():
    users = generate_users()
    products = generate_products()
    events = generate_data()

    events = inject_noise(events)

    users.to_csv("users.csv", index=False)
    products.to_csv("products.csv", index=False)
    events.to_csv("events.csv", index=False)

    print("✅ Generated users.csv, products.csv, events.csv")

if __name__ == "__main__":
    main()