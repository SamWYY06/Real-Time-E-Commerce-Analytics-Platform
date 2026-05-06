import pandas as pd
import numpy as np

n = 10000

data = pd.DataFrame({
    "user_id": np.random.randint(1, 1000, n),
    "event_type": np.random.choice(["view", "click", "purchase"], n),
    "product_id": np.random.randint(1, 500, n),
    "price": np.round(np.random.uniform(5, 500, n), 2),
    "timestamp": np.arange(n)
})

# ---------------------------
# 🧨 INTRODUCE MESSY DATA
# ---------------------------

# 1. NULL VALUES (missing data)
for col in ["user_id", "price"]:
    null_indices = np.random.choice(n, size=int(0.05 * n), replace=False)
    data.loc[null_indices, col] = np.nan

# 2. OUTLIERS (extreme values in price)
outlier_indices = np.random.choice(n, size=int(0.02 * n), replace=False)
data.loc[outlier_indices, "price"] = np.random.uniform(1000, 10000, size=len(outlier_indices))

# 3. DUPLICATES (repeat rows)
duplicate_rows = data.sample(frac=0.02)
data = pd.concat([data, duplicate_rows], ignore_index=True)

# 4. WRONG / BAD VALUES (data corruption simulation)
bad_indices = np.random.choice(len(data), size=int(0.01 * len(data)), replace=False)
data.loc[bad_indices, "event_type"] = "unknown_event"

# 5. NEGATIVE VALUES (invalid business logic)
neg_indices = np.random.choice(len(data), size=int(0.01 * len(data)), replace=False)
data.loc[neg_indices, "price"] = -abs(data.loc[neg_indices, "price"])

# ---------------------------
# 💾 SAVE DATA
# ---------------------------
data.to_csv("synthetic_data.csv", index=False)

print("Generated messy synthetic dataset with 10,000+ rows successfully!")