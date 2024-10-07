from __future__ import annotations

import logging
import os
import random
import sys
from datetime import datetime
from datetime import timedelta

import great_expectations as gx
import pandas as pd
from great_expectations.core.batch import BatchRequest
from great_expectations.dataset.pandas_dataset import PandasDataset

from airflow.decorators import dag
from airflow.decorators import task
from airflow.exceptions import AirflowFailException
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.utils.dates import days_ago


RAW_DATA_PATH = os.getenv("GOOD_DATA_PATH") or "data/raw_data"
PROCESSED_FILES_KEY = os.getenv("PROCESSED_FILES_KEY") or "process_files"
API_URL = os.getenv("API_URL") or "http://localhost:8000/"

ge_directory = os.getenv("GE_DIRECTORY") or "gx"
ge_directory = os.path.abspath(ge_directory)
context = gx.get_context(context_root_dir=ge_directory)
expectation_suite_name = "heart_disease_validation_suite"


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
        try:
            files = [
                file
                for file in os.listdir(RAW_DATA_PATH)
                if file.endswith(".csv")
            ]
        except Exception as e:
            raise AirflowFailException(f"Directory not found. {e}")

        if not files:
            logging.info(
                "No CSV files found in directory, skipping task.", sys.path
            )
            raise AirflowSkipException("No CSV files found in directory.")
        else:
            selected_file = random.choice(files)
            file_path = os.path.join(RAW_DATA_PATH, selected_file)
            logging.info(f"Selected file: {file_path}")

            data_to_ingest_df = pd.read_csv(file_path)

            os.remove(file_path)
            logging.info(f"File {file_path} has been deleted after ingestion.")
            return data_to_ingest_df

    @task
    def validate_data(data_to_ingest_df: pd.DataFrame) -> None:
        # expectation_suite = context.get_expectation_suite(expectation_suite_name)

        # checkpoint = context.add_or_update_checkpoint
        # (name="validation_checkpoint",validator=expectation_suite)
        # validator = context.sources.add_pandas
        # ("taxi_datasource").read_dataframe(
        #     df, asset_name="taxi_frame",
        # batch_metadata={"year": "2019", "month": "01"}
        # )
        # validator.save_expectation_suite()
        # # this allows the checkpoint to reference the expectation suite

        # checkpoint = context.add_or_update_checkpoint(
        #     name="my_taxi_validator_checkpoint", validator=validator
        # )

        # checkpoint_result = checkpoint.run()
        # ge_df = PandasDataset(data_to_ingest_df)
        # ge_df._initialize_expectations(expectation_suite)
        # validation_results = ge_df.validate()
        # print('validation_results:', validation_results)
        # context.run_checkpoint()
        # if data_to_ingest_df.empty:
        #     logging.info("No data to ingest, skipping task.")
        #     raise AirflowSkipException("No data to ingest.")

        # # data_asset_name = os.path.basename(file_path).split(".")[0]

        # file_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        # filepath = f"data/good_data/{file_name}"
        # logging.info(f"Ingesting data to the file: {filepath}")
        # files = Variable.get(
        #     PROCESSED_FILES_KEY, default_var=[], deserialize_json=True
        # )
        # files.append(file_name)
        # Variable.set(PROCESSED_FILES_KEY, files, serialize_json=True)
        # data_to_ingest_df.to_csv(filepath, index=False)
        return ""

    @task
    def send_alerts(data_to_ingest_df: pd.DataFrame) -> None:
        if data_to_ingest_df.empty:
            logging.info("No data to ingest, skipping task.")
            raise AirflowSkipException("No data to ingest.")

        file_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        filepath = f"data/good_data/{file_name}"
        logging.info(f"Ingesting data to the file: {filepath}")
        files = Variable.get(
            PROCESSED_FILES_KEY, default_var=[], deserialize_json=True
        )
        files.append(file_name)
        Variable.set(PROCESSED_FILES_KEY, files, serialize_json=True)
        data_to_ingest_df.to_csv(filepath, index=False)

    @task
    def save_file(data_to_ingest_df: pd.DataFrame) -> None:
        if data_to_ingest_df.empty:
            logging.info("No data to ingest, skipping task.")
            raise AirflowSkipException("No data to ingest.")

        file_name = f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv'
        filepath = f"data/good_data/{file_name}"
        logging.info(f"Ingesting data to the file: {filepath}")
        files = Variable.get(
            PROCESSED_FILES_KEY, default_var=[], deserialize_json=True
        )
        files.append(file_name)
        Variable.set(PROCESSED_FILES_KEY, files, serialize_json=True)
        data_to_ingest_df.to_csv(filepath, index=False)

    @task
    def save_statistics(data_to_ingest_df: pd.DataFrame) -> None:
        return "ss"

    data_to_ingest = read_data()
    validate_data(data_to_ingest)


ingest_data_dag = ingest_data()
