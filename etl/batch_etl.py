import pandas as pd
from datetime import datetime
from collections import defaultdict
import json
import math

from database.connection import get_connection


# ----------------------------
# EXTRACT
# ----------------------------
def extract_data(file_path):
    return pd.read_csv(file_path)


# ----------------------------
# SAFE JSON HANDLER
# ----------------------------
def clean_json_payload(obj):
    """
    Convert NaN → None so PostgreSQL JSON accepts it
    """
    cleaned = {}

    for k, v in obj.items():
        if isinstance(v, float) and math.isnan(v):
            cleaned[k] = None
        else:
            cleaned[k] = v

    return json.dumps(cleaned)


# ----------------------------
# DATE PARSER
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
# TRANSFORM (CLEAN + REJECT TRACKING)
# ----------------------------
def transform_data(df):

    original_len = len(df)
    reasons = defaultdict(int)

    rejected_rows = []

    df = df.drop_duplicates()

    # ---------------- TYPE CONVERSION ----------------
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # ---------------- MISSING VALUES ----------------
    mask = df["user_id"].isna()
    reasons["missing_user_id"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="missing_user_id"))
    df = df[~mask]

    mask = df["product_id"].isna()
    reasons["missing_product_id"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="missing_product_id"))
    df = df[~mask]

    mask = df["price"].isna()
    reasons["missing_price"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="missing_price"))
    df = df[~mask]

    # ---------------- TYPE SAFETY ----------------
    df["user_id"] = df["user_id"].astype(int)
    df["product_id"] = df["product_id"].astype(int)

    # ---------------- EVENT TYPE ----------------
    valid_events = ["view", "click", "purchase"]

    mask = ~df["event_type"].isin(valid_events)
    reasons["invalid_event_type"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="invalid_event_type"))
    df = df[~mask]

    # ---------------- PRICE ----------------
    mask = df["price"] <= 0
    reasons["non_positive_price"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="non_positive_price"))
    df = df[~mask]

    # ---------------- PRODUCT RANGE ----------------
    mask = (df["product_id"] < 1) | (df["product_id"] > 70)
    reasons["invalid_product_id_out_of_range"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="invalid_product_id_out_of_range"))
    df = df[~mask]

    # ---------------- USER VALIDATION ----------------
    mask = df["user_id"] <= 0
    reasons["invalid_user_id"] += mask.sum()
    rejected_rows.append(df[mask].assign(reason="invalid_user_id"))
    df = df[~mask]

    rejected_df = pd.concat(rejected_rows, ignore_index=True) if rejected_rows else pd.DataFrame()

    return df, rejected_df, reasons, original_len

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
            (event_id, user_id, product_id, date_id, product_name,
             event_type, price, event_timestamp, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING
        """, (
            str(row["event_id"]),
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
# REJECTED EVENTS LOADER
# ----------------------------
def load_rejected_events(cursor, rejected_df):

    if rejected_df.empty:
        return

    for _, row in rejected_df.iterrows():

        cursor.execute("""
            INSERT INTO rejected_events (event_id, reason, raw_payload)
            VALUES (%s, %s, %s)
        """, (
            str(row.get("event_id", "unknown")),
            row["reason"],
            clean_json_payload(row.to_dict()),
            "batch"
        ))

# ----------------------------
# LOAD PIPELINE
# ----------------------------
def load_data(df, rejected_df):

    conn = get_connection()
    cursor = conn.cursor()

    load_dim_user(cursor, df)
    load_dim_product(cursor, df)
    load_dim_date(cursor, df)

    load_fact(cursor, df)
    load_rejected_events(cursor, rejected_df)

    conn.commit()
    cursor.close()
    conn.close()

def log_batch_metrics(cursor, total, inserted, dropped):

    cursor.execute("""
        INSERT INTO data_quality_metrics
        (source, total_events, inserted_events, dropped_events)
        VALUES (%s, %s, %s, %s)
    """, (
        "batch",
        total,
        inserted,
        dropped
    ))
# ----------------------------
# LOGGING RAW EVENTS
# ----------------------------
def log_raw_batch(cursor, df):

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO raw_events (event_id, payload, source)
            VALUES (%s, %s, %s)
        """, (
            str(row.get("event_id", "unknown")),
            clean_json_payload(row.to_dict()),
            "batch"
        ))

# ----------------------------
# BATCH AGGREGATIONS
# ----------------------------
def run_batch_aggregations(cursor):

    # Daily sales
    cursor.execute("""
        INSERT INTO agg_daily_sales (date_id, total_revenue, total_orders)
        SELECT
            date_id,
            SUM(price),
            COUNT(*)
        FROM fact_ecommerce_events
        WHERE event_type = 'purchase'
        GROUP BY date_id
        ON CONFLICT (date_id)
        DO UPDATE SET
            total_revenue = EXCLUDED.total_revenue,
            total_orders = EXCLUDED.total_orders,
            updated_at = CURRENT_TIMESTAMP
    """)

    # Product performance
    cursor.execute("""
        INSERT INTO agg_product_performance
        (product_id, total_views, total_clicks, total_purchases, total_revenue)
        SELECT
            product_id,
            COUNT(*) FILTER (WHERE event_type = 'view'),
            COUNT(*) FILTER (WHERE event_type = 'click'),
            COUNT(*) FILTER (WHERE event_type = 'purchase'),
            SUM(price) FILTER (WHERE event_type = 'purchase')
        FROM fact_ecommerce_events
        GROUP BY product_id
        ON CONFLICT (product_id)
        DO UPDATE SET
            total_views = EXCLUDED.total_views,
            total_clicks = EXCLUDED.total_clicks,
            total_purchases = EXCLUDED.total_purchases,
            total_revenue = EXCLUDED.total_revenue,
            updated_at = CURRENT_TIMESTAMP
    """)

# ----------------------------
# RUN BATCH ETL
# ----------------------------
def run_batch_etl():

    print("🚀 BATCH ETL STARTED")

    # ----------------------------
    # EXTRACT
    # ----------------------------
    df = extract_data("data/raw/synthetic_data.csv")
    original_len = len(df)

    print(f"📦 Raw rows: {original_len}")

    # ----------------------------
    # TRANSFORM
    # ----------------------------
    df_clean, rejected_df, reasons, original_len = transform_data(df)

    inserted = len(df_clean)
    dropped = original_len - inserted

    print(f"🧹 Cleaned rows: {inserted}")
    print(f"❌ Dropped rows: {dropped}")

    print("\n🚨 DROP REASONS")
    for k, v in reasons.items():
        print(f" - {k}: {v}")

    # ----------------------------
    # DB CONNECTION
    # ----------------------------
    conn = get_connection()
    cursor = conn.cursor()
    # LOG RAW DATA FIRST
    log_raw_batch(cursor, df)

    try:
        # ----------------------------
        # LOG DATA QUALITY METRICS
        # ----------------------------
        cursor.execute("""
            INSERT INTO data_quality_metrics
            (source, total_events, inserted_events, dropped_events)
            VALUES (%s, %s, %s, %s)
        """, (
            "batch",
            original_len,
            inserted,
            dropped
        ))

        conn.commit()  # commit metrics separately

        # ----------------------------
        # LOAD DATA
        # ----------------------------
        load_dim_user(cursor, df_clean)
        load_dim_product(cursor, df_clean)
        load_dim_date(cursor, df_clean)

        load_fact(cursor, df_clean)

        if not rejected_df.empty:
            for _, row in rejected_df.iterrows():
                cursor.execute("""
                    INSERT INTO rejected_events (event_id, reason, raw_payload, source)
                    VALUES (%s, %s, %s, %s)
                """, (
                    str(row.get("event_id", "unknown")),
                    row["reason"],
                    clean_json_payload(row.to_dict()),
                    "batch"
                )) 
        run_batch_aggregations(cursor)

        conn.commit()

        print("✅ Batch ETL Completed")

    except Exception as e:
        conn.rollback()
        print("❌ Batch ETL Failed:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_batch_etl()