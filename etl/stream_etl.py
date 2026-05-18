import json
from kafka import KafkaConsumer
from datetime import datetime
from collections import defaultdict

from database.connection import get_connection


# ----------------------------
# CONSUMER
# ----------------------------
consumer = KafkaConsumer(
    "ecommerce-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)


# ----------------------------
# CLEAN EVENT
# ----------------------------
def clean_event(event):

    reasons = None
    VALID_PRODUCT_RANGE = (1, 70)

    required = ["user_id", "product_id", "event_type", "timestamp"]

    # ---------------- MISSING FIELD CHECK FIRST ----------------
    for f in required:
        if f not in event or event[f] is None:
            return None, f"missing_{f}"

    # ---------------- TYPE VALIDATION (SEPARATED) ----------------
    if not isinstance(event["user_id"], int):
        return None, "user_id_type_error"

    if not isinstance(event["product_id"], int):
        return None, "product_id_type_error"

    if "price" not in event:
        return None, "missing_price"

    # ---------------- EVENT TYPE ----------------
    valid_events = ["view", "click", "purchase"]

    if event["event_type"] not in valid_events:
        return None, "invalid_event_type"

    # ---------------- PRICE TYPE ----------------
    try:
        event["price"] = float(event["price"])
    except:
        return None, "price_type_error"

    if not (VALID_PRODUCT_RANGE[0] <= event["product_id"] <= VALID_PRODUCT_RANGE[1]):
        return None, "invalid_product_id_out_of_range"

    # ---------------- BUSINESS RULES ----------------
    if event["user_id"] <= 0:
        return None, "invalid_user_id"

    if event["product_id"] <= 0:
        return None, "invalid_product_id"

    if event["price"] < 0:
        return None, "negative_price"

    # ---------------- KEEP PRICE ALWAYS ----------------
    # DO NOT ZERO IT OUT
    return event, None


# ----------------------------
# DATE HELP
# ----------------------------
def parse_date(ts):
    dt = datetime.fromtimestamp(ts)
    return {
        "date_id": int(dt.strftime("%Y%m%d")),
        "dt": dt
    }


# ----------------------------
# DIMENSIONS
# ----------------------------
def ensure_user(cursor, e):
    cursor.execute("""
        INSERT INTO dim_user (user_id, user_segment, country, signup_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
        user_segment = EXCLUDED.user_segment,
        country = EXCLUDED.country,
        signup_date = EXCLUDED.signup_date
    """, (
        e["user_id"],
        e.get("user_segment", "unknown"),  
        e.get("country", "unknown"),       
        e.get("signup_date", None)         
    ))


def ensure_product(cursor, e):
    cursor.execute("""
        INSERT INTO dim_product (product_id, product_name, category, brand, price)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            brand = EXCLUDED.brand,
            price = EXCLUDED.price
    """, (
        e["product_id"],
        e.get("product_name", "unknown"),
        e.get("category", "unknown"),
        e.get("brand", "unknown"),
        e.get("price", 0)
    ))

def ensure_date(cursor, ts):
    d = parse_date(ts)

    cursor.execute("""
        INSERT INTO dim_date (date_id, full_date, day, month, year, weekday)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (date_id) DO NOTHING
    """, (
        d["date_id"],
        d["dt"].date(),
        d["dt"].day,
        d["dt"].month,
        d["dt"].year,
        d["dt"].strftime("%A")
    ))


# ----------------------------
# FACT INSERT
# ----------------------------
def insert_event(cursor, event, conn):
    try:
        ensure_user(cursor, event)
        conn.commit()

        ensure_product(cursor, event)
        conn.commit()

        ensure_date(cursor, event["timestamp"])
        conn.commit()

        d = parse_date(event["timestamp"])

        cursor.execute("""
            INSERT INTO fact_ecommerce_events
            (event_id, user_id, product_id, date_id, product_name,
             event_type, price, event_timestamp, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (event_id) DO NOTHING
        """, (
            event["event_id"],
            event["user_id"],
            event["product_id"],
            d["date_id"],
            event.get("product_name", "unknown"),
            event["event_type"],
            event["price"],
            datetime.fromtimestamp(event["timestamp"]),
            "stream"
        ))
        update_daily_sales(cursor, event)
        update_product_performance(cursor, event)

        conn.commit()  # final commit

    except Exception as e:
        print("❌ Insert failed:", e)
# ----------------------------
# LOGGING REJECTED EVENTS
# ----------------------------
def log_rejected_event(cursor, event, reason):
    try:

        # Ensure event is dict
        if not isinstance(event, dict):
            event = {"raw_value": str(event)}

        # Safe JSON (handles weird types + %)
        payload = json.dumps(event, default=str)

        cursor.execute("""
            INSERT INTO rejected_events (event_id, reason, raw_payload, source)
            VALUES (%s, %s, %s, %s)
        """, (
            str(event.get("event_id", "unknown")),
            str(reason),
            payload,
            "stream"
        ))

    except Exception as e:
        print("\n❌ Failed to log rejected event:", e)
        print("Event was:", event)
        cursor.connection.rollback()

# ----------------------------
# DATA QUALITY METRICS LOGGING
# ----------------------------        
def log_quality_metrics(cursor, processed, inserted, dropped):

    drop_rate = dropped / processed if processed > 0 else 0

    cursor.execute("""
        INSERT INTO data_quality_metrics
        (source, total_events, inserted_events, dropped_events)
        VALUES (%s, %s, %s, %s)
    """, (
        "stream",
        processed,
        inserted,
        dropped
    ))

    print(f"📉 Drop rate: {drop_rate:.2%}")

# ----------------------------
# LOGGING RAW EVENTS (OPTIONAL)
# ----------------------------   
def log_raw_event(cursor, event):
    try:
        cursor.execute("""
            INSERT INTO raw_events (event_id, payload, source)
            VALUES (%s, %s, %s)
        """, (
            str(event.get("event_id", "unknown")),
            json.dumps(event, default=str),
            "stream"
        ))
    except Exception as e:
        print("❌ Failed to log raw event:", e)

# ----------------------------
# AGGREGATIONS (OPTIONAL)
# ---------------------------- 
def update_daily_sales(cursor, event):

    if event["event_type"] != "purchase":
        return

    d = parse_date(event["timestamp"])

    cursor.execute("""
        INSERT INTO agg_daily_sales (date_id, total_revenue, total_orders)
        VALUES (%s, %s, %s)
        ON CONFLICT (date_id)
        DO UPDATE SET
            total_revenue = agg_daily_sales.total_revenue + EXCLUDED.total_revenue,
            total_orders = agg_daily_sales.total_orders + 1,
            updated_at = CURRENT_TIMESTAMP
    """, (
        d["date_id"],
        event["price"],
        1
    ))

def update_product_performance(cursor, event):

    views = 1 if event["event_type"] == "view" else 0
    clicks = 1 if event["event_type"] == "click" else 0
    purchases = 1 if event["event_type"] == "purchase" else 0
    revenue = event["price"] if event["event_type"] == "purchase" else 0

    cursor.execute("""
        INSERT INTO agg_product_performance
        (product_id, total_views, total_clicks, total_purchases, total_revenue)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (product_id)
        DO UPDATE SET
            total_views = agg_product_performance.total_views + EXCLUDED.total_views,
            total_clicks = agg_product_performance.total_clicks + EXCLUDED.total_clicks,
            total_purchases = agg_product_performance.total_purchases + EXCLUDED.total_purchases,
            total_revenue = agg_product_performance.total_revenue + EXCLUDED.total_revenue,
            updated_at = CURRENT_TIMESTAMP
    """, (
        event["product_id"],
        views,
        clicks,
        purchases,
        revenue
    ))

# ----------------------------
# STREAM RUNNER
# ----------------------------
def run_stream_etl():

    conn = get_connection()
    cursor = conn.cursor()

    processed = 0
    inserted = 0
    dropped = 0
    reasons = defaultdict(int)

    BATCH_SIZE = 20  # commit every 20 events

    print("⚡ STREAM ETL STARTED")

    for msg in consumer:

        processed += 1
        event = msg.value

        # Store Raw Events First
        log_raw_event(cursor, event)

        cleaned, reason = clean_event(event)

        if cleaned:
            insert_event(cursor, cleaned, conn)
            inserted += 1
        else:
            dropped += 1
            reasons[reason] += 1
            log_rejected_event(cursor, event, reason)

        # Batch commit + metrics logging
        if processed % BATCH_SIZE == 0:
            conn.commit()  # commit ETL work first

            log_quality_metrics(cursor, processed, inserted, dropped)
            conn.commit()  # commit metrics

        # 📊 Stats print
        if processed % 1 == 0:
            print(f"""
📊 STREAM STATS
Processed: {processed}
Inserted: {inserted}
Dropped: {dropped}
""")

            print("🚨 DROP REASONS")
            for k, v in reasons.items():
                print(f" - {k}: {v}")

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    run_stream_etl()