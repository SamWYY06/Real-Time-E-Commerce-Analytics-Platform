CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    user_id INT,
    event_type VARCHAR(50),
    product_id INT,
    price FLOAT,
    timestamp BIGINT
);
