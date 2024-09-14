from __future__ import annotations

import logging
from datetime import datetime
from datetime import timedelta

import pandas as pd

from airflow.decorators import dag
from airflow.decorators import task
from airflow.utils.dates import days_ago


@dag(
    dag_id="ingest_data",
    description="Ingest data from a file to another DAG",
    tags=["dsp", "data_ingestion"],
    schedule=timedelta(minutes=2),
    start_date=days_ago(n=0, hour=1),  # sets the starting point of the DAG
    max_active_runs=1,  # Ensure only one active run at a time
)
def ingest_data():
    @task
    def get_data_to_ingest_from_local_file() -> pd.DataFrame:
        nb_rows = 5
        filepath = "data/data.csv"
        input_data_df = pd.read_csv(filepath)
        logging.info(f"Extract {nb_rows} rows from the file {filepath}")
        data_to_ingest_df = input_data_df.sample(n=nb_rows)
        return data_to_ingest_df

    @task
    def save_data(data_to_ingest_df: pd.DataFrame) -> None:
        filepath = (
            f'data/raw_data/{datetime.now().strftime("%Y-%M-%d_%H-%M-%S")}.csv'
        )
        logging.info(f"Ingesting data to the file: {filepath}")
        data_to_ingest_df.to_csv(filepath, index=False)

    # Task relationships
    data_to_ingest = get_data_to_ingest_from_local_file()
    save_data(data_to_ingest)


ingest_data_dag = ingest_data()
