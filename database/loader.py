# =========================================================
# POSTGRESQL DATA LOADER
# =========================================================

from database.connection import get_connection

def insert_event(event, source):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO fact_ecommerce_events
        (user_id, product_id, event_type, price, event_timestamp, source)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        event["user_id"],
        event["product_id"],
        event["event_type"],
        event["price"],
        int(event["timestamp"]),
        source
    ))

    conn.commit()
    cursor.close()
    conn.close()