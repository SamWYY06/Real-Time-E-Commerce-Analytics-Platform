import pandas as pd
from datetime import datetime
from collections import defaultdict

from database.connection import get_connection


# ----------------------------
# EXTRACT
# ----------------------------
def extract_data(file_path):
    return pd.read_csv(file_path)


# ----------------------------
# TRANSFORM
# ----------------------------
def transform_data(df):

    original_len = len(df)
    reasons = defaultdict(int)

    df = df.drop_duplicates()

    # numeric conversion
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # missing values
    reasons["missing_user_id"] += df["user_id"].isna().sum()
    reasons["missing_product_id"] += df["product_id"].isna().sum()
    reasons["missing_price"] += df["price"].isna().sum()

    df = df.dropna(subset=["user_id", "product_id", "price"])

    # event validation
    valid_events = ["view", "click", "purchase"]
    reasons["invalid_event_type"] += (~df["event_type"].isin(valid_events)).sum()
    df = df[df["event_type"].isin(valid_events)]

    # price rules
    reasons["non_positive_price"] += (df["price"] <= 0).sum()
    df = df[df["price"] > 0]

    return df, reasons, original_len


# ----------------------------
# DATE DIM
# ----------------------------
def parse_date(ts):
    dt = datetime.fromtimestamp(ts)
    return {
        "date_id": int(dt.strftime("%Y%m%d")),
        "full_date": dt.date(),
        "day": dt.day,
        "month": dt.month,
        "year": dt.year,
        "weekday": dt.strftime("%A")
    }


# ----------------------------
# DIM: USER
# ----------------------------
def load_dim_user(cursor, df):

    users = df[["user_id", "user_segment", "country", "signup_date"]].drop_duplicates()

    for _, row in users.iterrows():
        cursor.execute("""
            INSERT INTO dim_user (user_id, user_segment, country, signup_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                user_segment = EXCLUDED.user_segment,
                country = EXCLUDED.country,
                signup_date = EXCLUDED.signup_date
        """, (
            int(row["user_id"]),
            row.get("user_segment", "unknown"),
            row.get("country", "unknown"),
            row.get("signup_date", None)
        ))


# ----------------------------
# DIM: PRODUCT
# ----------------------------
def load_dim_product(cursor, df):

    products = df[["product_id", "product_name", "category", "brand", "price"]].drop_duplicates()

    for _, row in products.iterrows():
        cursor.execute("""
            INSERT INTO dim_product (product_id, product_name, category, brand, price)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                category = EXCLUDED.category,
                brand = EXCLUDED.brand,
                price = EXCLUDED.price
        """, (
            int(row["product_id"]),
            row["product_name"],
            row["category"],
            row["brand"],
            float(row["price"])
        ))


# ----------------------------
# DIM: DATE
# ----------------------------
def load_dim_date(cursor, df):

    timestamps = df["timestamp"].drop_duplicates()

    for ts in timestamps:
        d = parse_date(ts)

        cursor.execute("""
            INSERT INTO dim_date (date_id, full_date, day, month, year, weekday)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (date_id) DO NOTHING
        """, (
            d["date_id"],
            d["full_date"],
            d["day"],
            d["month"],
            d["year"],
            d["weekday"]
        ))


# ----------------------------
# FACT TABLE
# ----------------------------
def load_fact(cursor, df):

    for _, row in df.iterrows():

        dt = datetime.fromtimestamp(row["timestamp"])
        date_id = int(dt.strftime("%Y%m%d"))

        cursor.execute("""
            INSERT INTO fact_ecommerce_events
            (user_id, product_id, date_id, product_name,
             event_type, price, event_timestamp, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            int(row["user_id"]),
            int(row["product_id"]),
            date_id,
            row["product_name"],
            row["event_type"],
            float(row["price"]),
            dt,
            "batch"
        ))


# ----------------------------
# LOAD ORCHESTRATOR
# ----------------------------
def load_data(df):

    conn = get_connection()
    cursor = conn.cursor()

    # DIMENSIONS FIRST (important for FK integrity)
    load_dim_user(cursor, df)
    load_dim_product(cursor, df)
    load_dim_date(cursor, df)

    # FACT TABLE
    load_fact(cursor, df)

    conn.commit()
    cursor.close()
    conn.close()


# ----------------------------
# RUN BATCH ETL
# ----------------------------
def run_batch_etl():

    print("🚀 BATCH ETL STARTED")

    df = extract_data("data/raw/synthetic_data.csv")

    print(f"📦 Raw rows: {len(df)}")

    df_clean, reasons, original_len = transform_data(df)

    print(f"🧹 Cleaned rows: {len(df_clean)}")
    print(f"❌ Dropped rows: {original_len - len(df_clean)}")

    print("\n🚨 DROP REASONS")
    for k, v in reasons.items():
        print(f" - {k}: {v}")

    load_data(df_clean)

    print("✅ Batch ETL Completed")


if __name__ == "__main__":
    run_batch_etl()