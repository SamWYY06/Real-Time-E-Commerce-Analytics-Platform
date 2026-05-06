CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    country VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    price NUMERIC(10,2)
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,

    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),

    event_type VARCHAR(50),

    event_timestamp INT
);