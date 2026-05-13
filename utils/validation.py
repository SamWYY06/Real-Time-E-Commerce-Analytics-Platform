def validate_event(event):

    required_fields = ["user_id", "product_id", "event_type", "price"]

    for field in required_fields:
        if field not in event:
            return False

    if event["price"] <= 0:
        return False

    return True