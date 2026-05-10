-- TABLES DESIGN

-- USED FOR ANALYZING USER BEHAVIOR, PRODUCT PERFORMANCE, AND SALES TRENDS
CREATE TABLE dim_user (
    user_id INT PRIMARY KEY,
    user_segment VARCHAR(50),
    country VARCHAR(100),
    signup_date DATE
);

-- USED FOR ANALYZING PRODUCT PERFORMANCE, CATEGORIZATION, AND PRICING STRATEGIES
CREATE TABLE dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price FLOAT
);

-- GROUP BY DAY, MONTH, YEAR, WEEKDAY
CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE,
    day INT,
    month INT,
    year INT,
    weekday VARCHAR(20)
);

-- MAIN TABLE FOR ANALYTICS, CONTAINING ALL EVENTS
CREATE TABLE fact_ecommerce_events (
    event_id SERIAL PRIMARY KEY,

    user_id INT REFERENCES dim_user(user_id),
    product_id INT REFERENCES dim_product(product_id),
    date_id INT REFERENCES dim_date(date_id),

    product_name VARCHAR(255),

    event_type VARCHAR(50),
    price FLOAT,
    event_timestamp TIMESTAMP,
    source VARCHAR(20)
);
