# Stores user information
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    country VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

# Stores product details.
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(150),
    category VARCHAR(100),
    price NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

# Stores event information.
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,

    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),

    event_type VARCHAR(50),   -- view / click / purchase
    quantity INT DEFAULT 1,

    revenue NUMERIC(10,2),    -- only meaningful for purchase events

    event_timestamp TIMESTAMPTZ
);