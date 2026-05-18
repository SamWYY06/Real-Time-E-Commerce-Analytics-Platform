-- TABLES DESIGN

-- USED FOR ANALYZING USER BEHAVIOR, PRODUCT PERFORMANCE, AND SALES TRENDS
CREATE TABLE IF NOT EXISTS dim_user (
    user_id INT PRIMARY KEY,
    user_segment VARCHAR(50),
    country VARCHAR(100),
    signup_date DATE
);

-- USED FOR ANALYZING PRODUCT PERFORMANCE, CATEGORIZATION, AND PRICING STRATEGIES
CREATE TABLE IF NOT EXISTS dim_product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    brand VARCHAR(100),
    price FLOAT
);

-- GROUP BY DAY, MONTH, YEAR, WEEKDAY
CREATE TABLE IF NOT EXISTS dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE,
    day INT,
    month INT,
    year INT,
    weekday VARCHAR(20)
);

-- MAIN TABLE FOR ANALYTICS, CONTAINING ALL EVENTS
CREATE TABLE IF NOT EXISTS fact_ecommerce_events (
    event_id UUID PRIMARY KEY,

    user_id INT REFERENCES dim_user(user_id),
    product_id INT REFERENCES dim_product(product_id),
    date_id INT REFERENCES dim_date(date_id),

    product_name VARCHAR(255),

    event_type VARCHAR(50),
    price FLOAT,
    event_timestamp TIMESTAMP,
    source VARCHAR(20)
);

-- USED TO STORE EVENTS THAT FAILED VALIDATION OR PROCESSING, ALLOWING FOR LATER REVIEW AND ANALYSIS
CREATE TABLE IF NOT EXISTS rejected_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100),
    reason VARCHAR(255),
    raw_payload JSON,
    source VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- USED TO TRACK THE QUALITY OF THE DATA BEING PROCESSED, PROVIDING INSIGHTS INTO THE NUMBER OF EVENTS PROCESSED, INSERTED, AND DROPPED, AS WELL AS THE REASONS FOR ANY DROPPED EVENTS
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id SERIAL PRIMARY KEY,
    source VARCHAR(20),
    total_events INT,
    inserted_events INT,
    dropped_events INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USED TO STORE RAW EVENTS AS THEY ARE RECEIVED FROM THE STREAM, BEFORE ANY TRANSFORMATION OR VALIDATION, ALLOWING FOR AUDITING AND REPROCESSING IF NEEDED
CREATE TABLE IF NOT EXISTS raw_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100),
    payload JSON,
    source VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily revenue
CREATE TABLE IF NOT EXISTS agg_daily_sales (
    date_id INT PRIMARY KEY,
    total_revenue FLOAT,
    total_orders INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product performance
CREATE TABLE IF NOT EXISTS agg_product_performance (
    product_id INT PRIMARY KEY,
    total_views INT,
    total_clicks INT,
    total_purchases INT,
    total_revenue FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);