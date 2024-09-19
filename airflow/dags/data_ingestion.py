from __future__ import annotations

import logging
import os
import random
from datetime import datetime
from datetime import timedelta

import pandas as pd

from airflow.decorators import dag
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.utils.dates import days_ago

RAW_DATA_PATH = "data/raw_data"
PROCESS_FILES_KEY = "process_files"


@dag(
    dag_id="data_ingestion",
    description="Ingest data from a file to another DAG",
    tags=["dsp", "data_ingestion"],
    schedule=timedelta(minutes=1),
    start_date=days_ago(0),  # sets the starting point of the DAG
    max_active_runs=1,  # Ensure only one active run at a time
)
def ingest_data():
    @task
    def read_data() -> pd.DataFrame:
        files = [
            file for file in os.listdir(RAW_DATA_PATH) if file.endswith(".csv")
        ]
        if not files:
            logging.info("No CSV files found in directory, skipping task.")
            raise AirflowSkipException("No CSV files found in directory.")

        selected_file = random.choice(files)
        file_path = os.path.join(RAW_DATA_PATH, selected_file)
        logging.info(f"Selected file: {file_path}")

        data_to_ingest_df = pd.read_csv(file_path)

        os.remove(file_path)
        logging.info(f"File {file_path} has been deleted after ingestion.")
        return data_to_ingest_df

    @task
    def save_file(data_to_ingest_df: pd.DataFrame) -> None:
        file_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        filepath = f"data/good_data/{file_name}"
        logging.info(f"Ingesting data to the file: {filepath}")
        files = Variable.get(
            PROCESS_FILES_KEY, default_var=[], deserialize_json=True
        )
        files.append(file_name)
        Variable.set(PROCESS_FILES_KEY, files, serialize_json=True)
        logging.info(f"File {files} has been deleted after ingestion.")
        data_to_ingest_df.to_csv(filepath, index=False)

    data_to_ingest = read_data()
    save_file(data_to_ingest)


ingest_data_dag = ingest_data()
