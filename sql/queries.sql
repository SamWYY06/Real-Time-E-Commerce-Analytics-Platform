# ANALYTIC QUERIES
-- Total revenue
SELECT SUM(price) AS total_revenue
FROM fact_ecommerce_events
WHERE event_type = 'purchase';

-- Top products
SELECT product_id, COUNT(*) AS views
FROM fact_ecommerce_events
WHERE event_type = 'view'
GROUP BY product_id
ORDER BY views DESC;

-- Conversion rate
SELECT 
    COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) * 1.0 /
    COUNT(CASE WHEN event_type = 'view' THEN 1 END) AS conversion_rate
FROM fact_ecommerce_events;


-- Daily activity
SELECT 
    date_id,
    COUNT(*) AS total_events
FROM fact_ecommerce_events
GROUP BY date_id
ORDER BY date_id;

-- Business Analytics Queries
SELECT 
    date_id,
    SUM(price) AS daily_revenue
FROM fact_ecommerce_events
WHERE event_type = 'purchase'
GROUP BY date_id
ORDER BY date_id;

-- User analysis
SELECT user_segment, COUNT(*)
FROM fact_ecommerce_events f
JOIN dim_user u ON f.user_id = u.user_id
GROUP BY user_segment;

-- Time analysis
SELECT d.month, SUM(price)
FROM fact_ecommerce_events f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.month;