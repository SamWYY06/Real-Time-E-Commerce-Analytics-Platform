from airflow import DAG
from airflow.operators.python import PythonOperator # type: ignore
from datetime import datetime, timedelta

from etl.batch_etl import run_batch_etl

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 5, 7),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


def run_etl():
    print("Starting Batch ETL...")
    run_batch_etl()
    print("Batch ETL Finished.")


with DAG(
    dag_id="ecommerce_etl_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    batch_task = PythonOperator(
        task_id="run_batch_etl",
        python_callable=run_etl,
    )

    batch_task