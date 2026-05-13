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
        e["user_segment"],
        e["country"],
        e["signup_date"]
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
def insert_event(cursor, event):

    ensure_user(cursor, event)
    ensure_product(cursor, event)
    ensure_date(cursor, event["timestamp"])

    d = parse_date(event["timestamp"])

    cursor.execute("""
        INSERT INTO fact_ecommerce_events
        (user_id, product_id, date_id, product_name,
         event_type, price, event_timestamp, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        event["user_id"],
        event["product_id"],
        d["date_id"],
        event["product_name"],
        event["event_type"],
        event["price"],
        datetime.fromtimestamp(event["timestamp"]),
        "stream"
    ))

# ----------------------------
# LOGGING REJECTED EVENTS
# ----------------------------
def log_rejected_event(cursor, event, reason):
    try:
        cursor.execute("""
            INSERT INTO rejected_events (event_id, reason, raw_payload)
            VALUES (%s, %s, %s)
        """, (
            str(event.get("event_id", "unknown")),
            reason,
            json.dumps(event)
        ))
    except Exception as e:
        print("Failed to log rejected event:", e)



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

    BATCH_SIZE = 20  # commit every 50 events

    print("⚡ STREAM ETL STARTED")

    for msg in consumer:

        processed += 1
        event = msg.value

        cleaned, reason = clean_event(event)

        if cleaned:
            insert_event(cursor, cleaned)
            inserted += 1
        else:
            dropped += 1
            reasons[reason] += 1
            log_rejected_event(cursor, event, reason)

        # Batch commit
        if processed % BATCH_SIZE == 0:
            conn.commit()

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