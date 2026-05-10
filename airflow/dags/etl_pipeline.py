# SCHEDULED ETL JOBS
from airflow import DAG
from airflow.operators.python import PythonOperator # type: ignore
from datetime import datetime
import os

# import your ETL
from etl.batch_etl import run_batch_etl


default_args = {
    "start_date": datetime(2026, 05, 7),
    "retries": 1
}

dag = DAG(
    "ecommerce_etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
)


def run_etl():
    run_batch_etl()


task1 = PythonOperator(
    task_id="run_batch_etl",
    python_callable=run_etl,
    dag=dag
)

task1