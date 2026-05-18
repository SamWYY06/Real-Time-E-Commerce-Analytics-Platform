import random
import time
import uuid

PRODUCTS = [
    # ---------------- ELECTRONICS ----------------
    {"id": 1, "name": "iPhone 15", "category": "Electronics", "brand": "Apple", "price": 1200},
    {"id": 2, "name": "Samsung Galaxy S23", "category": "Electronics", "brand": "Samsung", "price": 1000},
    {"id": 3, "name": "MacBook Pro", "category": "Electronics", "brand": "Apple", "price": 2500},
    {"id": 4, "name": "Dell XPS 13", "category": "Electronics", "brand": "Dell", "price": 1800},
    {"id": 5, "name": "iPad Air", "category": "Electronics", "brand": "Apple", "price": 900},
    {"id": 6, "name": "Samsung Tablet", "category": "Electronics", "brand": "Samsung", "price": 700},
    {"id": 7, "name": "Sony Headphones", "category": "Electronics", "brand": "Sony", "price": 300},
    {"id": 8, "name": "AirPods Pro", "category": "Electronics", "brand": "Apple", "price": 250},
    {"id": 9, "name": "Smart Watch", "category": "Electronics", "brand": "Fitbit", "price": 400},
    {"id": 10, "name": "Gaming Laptop", "category": "Electronics", "brand": "Asus", "price": 2200},
    {"id": 11, "name": "Mechanical Keyboard", "category": "Electronics", "brand": "Logitech", "price": 150},
    {"id": 12, "name": "Wireless Mouse", "category": "Electronics", "brand": "Logitech", "price": 80},
    {"id": 13, "name": "4K Monitor", "category": "Electronics", "brand": "LG", "price": 600},
    {"id": 14, "name": "External SSD", "category": "Electronics", "brand": "Samsung", "price": 200},
    {"id": 15, "name": "Bluetooth Speaker", "category": "Electronics", "brand": "JBL", "price": 120},

    # ---------------- FASHION ----------------
    {"id": 16, "name": "Running Shoes", "category": "Fashion", "brand": "Nike", "price": 120},
    {"id": 17, "name": "Sneakers", "category": "Fashion", "brand": "Adidas", "price": 150},
    {"id": 18, "name": "Jeans", "category": "Fashion", "brand": "Levi's", "price": 80},
    {"id": 19, "name": "T-Shirt", "category": "Fashion", "brand": "Uniqlo", "price": 40},
    {"id": 20, "name": "Jacket", "category": "Fashion", "brand": "Zara", "price": 200},
    {"id": 21, "name": "Dress", "category": "Fashion", "brand": "H&M", "price": 120},
    {"id": 22, "name": "Hoodie", "category": "Fashion", "brand": "Puma", "price": 90},
    {"id": 23, "name": "Cap", "category": "Fashion", "brand": "Nike", "price": 30},
    {"id": 24, "name": "Sunglasses", "category": "Fashion", "brand": "Ray-Ban", "price": 180},
    {"id": 25, "name": "Leather Belt", "category": "Fashion", "brand": "Levi's", "price": 60},
    {"id": 26, "name": "Backpack", "category": "Fashion", "brand": "Adidas", "price": 100},
    {"id": 27, "name": "Sports Shorts", "category": "Fashion", "brand": "Nike", "price": 50},
    {"id": 28, "name": "Formal Shirt", "category": "Fashion", "brand": "Zara", "price": 90},
    {"id": 29, "name": "Sandals", "category": "Fashion", "brand": "Havaianas", "price": 70},
    {"id": 30, "name": "Watch", "category": "Fashion", "brand": "Casio", "price": 250},

    # ---------------- HOME ----------------
    {"id": 31, "name": "Coffee Maker", "category": "Home", "brand": "Philips", "price": 150},
    {"id": 32, "name": "Air Fryer", "category": "Home", "brand": "Xiaomi", "price": 180},
    {"id": 33, "name": "Vacuum Cleaner", "category": "Home", "brand": "Dyson", "price": 300},
    {"id": 34, "name": "Blender", "category": "Home", "brand": "Philips", "price": 100},
    {"id": 35, "name": "Rice Cooker", "category": "Home", "brand": "Panasonic", "price": 120},
    {"id": 36, "name": "Electric Kettle", "category": "Home", "brand": "Tefal", "price": 60},
    {"id": 37, "name": "Microwave Oven", "category": "Home", "brand": "Samsung", "price": 250},
    {"id": 38, "name": "Toaster", "category": "Home", "brand": "Philips", "price": 70},
    {"id": 39, "name": "Dining Table", "category": "Home", "brand": "Ikea", "price": 800},
    {"id": 40, "name": "Office Chair", "category": "Home", "brand": "Ikea", "price": 200},
    {"id": 41, "name": "Bed Frame", "category": "Home", "brand": "Ikea", "price": 900},
    {"id": 42, "name": "Sofa", "category": "Home", "brand": "Ikea", "price": 1200},
    {"id": 43, "name": "Desk Lamp", "category": "Home", "brand": "Philips", "price": 50},
    {"id": 44, "name": "Curtains", "category": "Home", "brand": "Ikea", "price": 120},
    {"id": 45, "name": "Wall Clock", "category": "Home", "brand": "Generic", "price": 40},

    # ---------------- BEAUTY ----------------
    {"id": 46, "name": "Face Cleanser", "category": "Beauty", "brand": "Nivea", "price": 30},
    {"id": 47, "name": "Moisturizer", "category": "Beauty", "brand": "Nivea", "price": 40},
    {"id": 48, "name": "Lipstick", "category": "Beauty", "brand": "Maybelline", "price": 25},
    {"id": 49, "name": "Perfume", "category": "Beauty", "brand": "Dior", "price": 150},
    {"id": 50, "name": "Shampoo", "category": "Beauty", "brand": "Dove", "price": 20},
    {"id": 51, "name": "Hair Dryer", "category": "Beauty", "brand": "Philips", "price": 80},
    {"id": 52, "name": "Makeup Kit", "category": "Beauty", "brand": "Maybelline", "price": 120},
    {"id": 53, "name": "Sunscreen", "category": "Beauty", "brand": "Nivea", "price": 35},
    {"id": 54, "name": "Body Lotion", "category": "Beauty", "brand": "Dove", "price": 25},
    {"id": 55, "name": "Nail Polish", "category": "Beauty", "brand": "O.P.I", "price": 15},

    # ---------------- SPORTS ----------------
    {"id": 56, "name": "Football", "category": "Sports", "brand": "Adidas", "price": 40},
    {"id": 57, "name": "Basketball", "category": "Sports", "brand": "Nike", "price": 50},
    {"id": 58, "name": "Tennis Racket", "category": "Sports", "brand": "Wilson", "price": 200},
    {"id": 59, "name": "Yoga Mat", "category": "Sports", "brand": "Decathlon", "price": 60},
    {"id": 60, "name": "Dumbbells", "category": "Sports", "brand": "Decathlon", "price": 150},
    {"id": 61, "name": "Treadmill", "category": "Sports", "brand": "Technogym", "price": 1500},
    {"id": 62, "name": "Cycling Helmet", "category": "Sports", "brand": "Giro", "price": 80},
    {"id": 63, "name": "Skipping Rope", "category": "Sports", "brand": "Decathlon", "price": 20},
    {"id": 64, "name": "Gym Bag", "category": "Sports", "brand": "Nike", "price": 90},
    {"id": 65, "name": "Water Bottle", "category": "Sports", "brand": "Stanley", "price": 25},

    # ---------------- BOOKS ----------------
    {"id": 66, "name": "Python Programming Book", "category": "Books", "brand": "O'Reilly", "price": 50},
    {"id": 67, "name": "Data Science Handbook", "category": "Books", "brand": "Packt", "price": 70},
    {"id": 68, "name": "Machine Learning Guide", "category": "Books", "brand": "O'Reilly", "price": 80},
    {"id": 69, "name": "Business Strategy Book", "category": "Books", "brand": "Harvard Press", "price": 60},
    {"id": 70, "name": "Self Development Book", "category": "Books", "brand": "Penguin", "price": 40},
]

EVENT_TYPES = ["view", "click", "purchase"]

COUNTRIES = ["Malaysia", "Singapore", "Indonesia", "Thailand", "Vietnam", "Philippines"]

USER_SEGMENTS = ["browser", "casual", "buyer"]

# ---------------- USER GENERATION ----------------
def generate_user():
    user_id = random.randint(1, 500)

    segment = random.choices(
        USER_SEGMENTS,
        weights=[0.5, 0.3, 0.2]
    )[0]

    country = random.choices(
        COUNTRIES,
        weights=[0.4, 0.2, 0.15, 0.15, 0.05, 0.05]
    )[0]

    # simulate realistic signup dates (last 2 years)
    signup_timestamp = int(time.time()) - random.randint(1, 60*60*24*365*2)
    signup_date = time.strftime("%Y-%m-%d", time.localtime(signup_timestamp))

    return user_id, segment, country, signup_date

# ---------------- CORE EVENT GENERATION ----------------
def generate_event(messy=False):

    user_id, segment, country, signup_date = generate_user()
    product = random.choice(PRODUCTS)

    # ---------------- EVENT TYPE ----------------
    if segment == "browser":
        event_type = random.choices(EVENT_TYPES, [0.8, 0.15, 0.05])[0]
    elif segment == "casual":
        event_type = random.choices(EVENT_TYPES, [0.5, 0.3, 0.2])[0]
    else:
        event_type = random.choices(EVENT_TYPES, [0.2, 0.3, 0.5])[0]

    # ALWAYS start from product price
    price = product["price"]

    # ---------------- EVENT OBJECT ----------------
    event = {
        "event_id": str(uuid.uuid4()),

        "user_id": user_id,
        "user_segment": segment,
        "country": country,
        "signup_date": signup_date,

        "product_id": product["id"],
        "product_name": product["name"],
        "brand": product["brand"],
        "category": product["category"],

        "event_type": event_type,
        "price": price, 
        "timestamp": int(time.time())
    }

    # ---------------- MESSY MODE ----------------
    if messy:

        # 15% missing user
        if random.random() < 0.15:
            event["user_id"] = None

        # 10% missing product
        if random.random() < 0.10:
            event["product_id"] = None

        # 10% invalid product range
        if random.random() < 0.10:
            event["product_id"] = random.randint(1000, 5000)

        # 10% invalid user type
        if random.random() < 0.10:
            event["user_id"] = "unknown_user"

        # 15% price inflation
        if random.random() < 0.15:
            event["price"] *= random.randint(2, 10)

        # 10% negative price
        if random.random() < 0.10:
            event["price"] = -abs(event["price"])

        # 10% invalid event type
        if random.random() < 0.10:
            event["event_type"] = "invalid"

        # 10% missing category
        if random.random() < 0.10:
            event.pop("category", None)
        # 5% missing price
        if random.random() < 0.05:
            event["price"] = None

        # 5% missing field entirely
        if random.random() < 0.05:
            event.pop("price", None)

    return event