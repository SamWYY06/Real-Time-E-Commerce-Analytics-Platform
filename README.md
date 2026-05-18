# Overview
# This project is a hybrid data pipeline that processes e-commerce events using both streaming (real-time) and batch (offline) ETL pipelines.

## It simulates a production-grade system with:

- Real-time ingestion via Kafka
- Batch ingestion from CSV files
- Data validation and rejection tracking
- Star schema data warehouse in PostgreSQL
- Data quality monitoring
- Business-level aggregations

# Architecture Components
1. Data Generator
## Generates synthetic e-commerce events
## Simulates user behavior such as view, click, and purchase events
- Produces:
    - Kafka stream events
    - CSV files for batch ingestion

2. Streaming ETL (Kafka → PostgreSQL)
## Processes events in real time.
- Steps:
    - Consume events from Kafka topic (ecommerce-events)
    - Store raw event in raw_events
    - Validate and clean data
- Route data:
    - Valid records → fact and dimension tables
    - Invalid records → rejected_events
- Update:
    - Data quality metrics
    - Aggregation tables (real-time KPIs)
3. Batch ETL (CSV → PostgreSQL)
## Processes historical data in bulk.
- Steps:
    - Extract data from CSV
    - Store raw data in raw_events
    - Transform and validate data
- Route data:
    - Valid records → fact and dimension tables
    - Invalid records → rejected_events
    - Log data quality metrics
    - Run aggregation queries
4. PostgreSQL Data Warehouse
    - Raw Layer
        - raw_events
## Stores all incoming data without filtering. Enables replay and debugging.
# Clean Layer (Star Schema)
## Fact Table
    - fact_ecommerce_events
    - Stores event-level transactional data

## Dimension Tables
    - dim_user
    - dim_product
    - dim_date
## Rejected Data
    - rejected_events
    # Stores invalid records with:
        - rejection reason
        - raw payload
        - data source (batch or stream)
## Data Quality Metrics
    - data_quality_metrics
    # Tracks:
        - total events
        - inserted events
        - dropped events
## Aggregation Layer
    - agg_daily_sales
    - agg_product_performance

5. Docker Setup
## The system is containerized using Docker.

## Services:
    - Kafka (event streaming)
    - Zookeeper (Kafka coordination)
    - PostgreSQL (data warehouse)

# End-to-End Data Flow
Data Generator
        |
        |----------------------|
        |                      |
   Kafka Stream           CSV Batch File
        |                      |
        v                      v
   Stream ETL             Batch ETL
        |                      |
        |------ raw_events ----|
                    |
                    v
           Data Validation Layer
                    |
            ---------------------
            |                   |
            v                   v
     Valid Events        Rejected Events
            |                   |
            v                   v
   Fact + Dimensions     rejected_events
            |
            v
        Aggregations
            |
            v
     Analytics / Dashboard




# File Flow
1. Ingestion (data_generator.py)
    - Stream Generator (stream_generator.py)
    - Batch Generator (batch_generator.py)
2. Kafka 
    - Consumers (consumer.py)
    - Producers (stream_etl.py)
3. ETL (cleaning)
    - Batch ETL (batch_etl.py)
    - Stream ETL (stream_etl.py)
4. SQL (queries)
    - Schemas (schema.sql)
    - Queries (queries.sql)
5. Database (database)
    - Connection (connection.py)
    - Loaders (loader.py)
6. Docker (Containerization)
    - Docker (docker-compose.yml)