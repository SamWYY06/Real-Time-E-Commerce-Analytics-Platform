# 📊 Real-Time E-Commerce Analytics Platform

## 🧠 Project Overview

This project is an end-to-end data engineering and analytics platform that simulates a real-world e-commerce system. It integrates batch processing and real-time streaming to ingest, transform, and analyze data using industry-standard tools.

The system processes data from APIs and synthetic generators, validates it using Postman, streams real-time events, and loads structured data into a data warehouse for analytics and visualization.

---

## 🎯 Objectives

- Build a scalable data engineering pipeline (batch + streaming)
- Simulate real-time e-commerce transactions
- Design and implement a data warehouse using SQL
- Automate workflows using orchestration tools
- Visualize insights using BI dashboards

---

## 🏗️ System Architecture

Data Sources (API / Synthetic Data) -> Python Ingestion Layer -> Apache Kafka (Streaming Layer) -> Python Consumer Processing -> PostgreSQL Data Warehouse -> Apache Airflow (Orchestration) -> Apache Spark (Big Data Processing) -> Power BI Dashboard ->

---

## 🛠️ Tech Stack

### Programming Languages
- Python
- SQL
- Bash / Shell Scripting

### Data Engineering Tools
- Apache Kafka (Event Streaming)
- Apache Airflow (Workflow Orchestration)
- Apache Spark (Big Data Processing)

### Databases
- PostgreSQL (Data Warehouse)
- NoSQL Database (Optional for raw data)

### Tools
- Postman (API Testing)
- Power BI (Data Visualization)
- GitHub / SourceTree (Version Control)

---

## 📦 Features

### 🔹 Data Ingestion
- API-based data extraction
- Synthetic real-time event generator
- Postman-tested endpoints

### 🔹 Streaming Pipeline
- Real-time event streaming using Kafka
- Producer-consumer architecture

### 🔹 Batch ETL Pipeline
- Data cleaning and transformation using Python
- SQL-based loading into data warehouse

### 🔹 Data Warehouse
- Star schema design (fact and dimension tables)
- Optimized SQL queries for analytics

### 🔹 Orchestration
- Automated workflows using Airflow DAGs
- Scheduling, monitoring, and retries

### 🔹 Analytics & Visualization
- Power BI dashboards:
  - Sales trends
  - Customer behavior
  - Real-time activity monitoring

---

## 📊 Sample Insights

- Top-selling products
- Revenue by region
- Customer segmentation
- Real-time user activity tracking

---

## 🚀 How to Run the Project

### 1. Clone Repository
```bash
git clone <repo-url>
cd project-folder
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Docker Services
```bash
docker-compose up -d
```

### 4. Run ETL Pipeline
```bash
python etl_pipeline.py
```

### 5. Start Kafka Producer
```bash
python producer.py
```

### 6. Start Airflow
```bash
airflow standalone
```

## 📁 Project Structure
project/
│
├── data/
├── ingestion/
├── kafka/
├── airflow_dags/
├── spark_jobs/
├── sql/
├── dashboard/
├── scripts/
├── docker-compose.yml
└── README.md

## 👥 Collaboration
This project is developed collaboratively using GitHub and SourceTree.

### Workflow
- Feature branching strategy
- Pull requests for code review
- Regular sync using git pull

## 📌 Key Learning Outcomes
- End-to-end data pipeline design
- Real-time streaming architecture
- Data warehouse modeling (SQL)
- Workflow orchestration with Airflow
- Big data processing with Spark
- BI dashboard development with Power BI

## 👨‍💻 Author
# Samuel Wong Yu Yang, Besty Tan Mei Yuh
# Data Engineering & Analytics Project
