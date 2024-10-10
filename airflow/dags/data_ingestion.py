from __future__ import annotations

import json
import logging
import os
import random
import sys
from datetime import datetime
from datetime import timedelta

import great_expectations as gx
import pandas as pd
import requests
from great_expectations.core.batch import BatchRequest
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import DataContext
from great_expectations.dataset.pandas_dataset import PandasDataset

from airflow.decorators import dag
from airflow.decorators import task
from airflow.exceptions import AirflowFailException
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.utils.dates import days_ago

# Import Great Expectations

# Define environment variables for paths
RAW_DATA_PATH = os.getenv("RAW_DATA_PATH") or "data/raw_data"
GOOD_DATA_PATH = os.getenv("GOOD_DATA_PATH") or "data/good_data"
BAD_DATA_PATH = os.getenv("GOOD_DATA_PATH") or "data/bad_data"

# Create directories if they don't exist
os.makedirs(GOOD_DATA_PATH, exist_ok=True)
os.makedirs(BAD_DATA_PATH, exist_ok=True)
os.makedirs(RAW_DATA_PATH, exist_ok=True)

# Define environment variables for configuration
PROCESSED_FILES_KEY = os.getenv("PROCESSED_FILES_KEY") or "process_files"
API_URL = os.getenv("API_URL") or "http://localhost:8000/"

# great_expectations configuration
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

            data_to_ingest_df_df = pd.read_csv(file_path)
            data_to_ingest_df_df.attrs["file_name"] = selected_file

            os.remove(file_path)
            logging.info(f"File {file_path} has been deleted after ingestion.")
            return data_to_ingest_df_df

    @task
    def validate_data(data_to_ingest_df_df: pd.DataFrame):
        # run_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        runtime_request = RuntimeBatchRequest(
            datasource_name="my_datasource",
            data_connector_name="default_runtime_data_connector_name",
            data_asset_name="my_runtime_asset_name",
            runtime_parameters={"batch_data": data_to_ingest_df_df},
            batch_identifiers={"default_identifier_name": "my_data"},
        )
        validator = context.get_validator(
            batch_request=runtime_request,
            expectation_suite_name=expectation_suite_name,
        )
        checkpoint_result = context.run_checkpoint(
            checkpoint_name="validation_checkpoint", validator=validator
        )
        return checkpoint_result

    @task
    def send_alerts(checkpoint_result, webhook_url: str) -> None:
        criticality = "high"
        summary = checkpoint_result["statistics"]["errors_summary"]
        report_link = checkpoint_result["meta"].get(
            "validation_report_url", "N/A"
        )

        alert_message = {
            "text": (
                f"Data Quality Alert - "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ),
            "attachments": [
                {
                    "title": "Data Quality Issues Detected",
                    "fields": [
                        {
                            "title": "Criticality",
                            "value": criticality,
                            "short": True,
                        },
                        {"title": "Summary", "value": summary, "short": False},
                        {
                            "title": "Link to Report",
                            "value": report_link,
                            "short": False,
                        },
                    ],
                    "color": "#FF0000" if criticality == "high" else "#FFFF00",
                }
            ],
        }

        # Send alert to the teams channel using a webhook
        response = requests.post(
            webhook_url,
            data=json.dumps(alert_message),
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            raise ValueError(
                f"Request to Teams webhook failed with status code "
                f"{response.status_code}, response: {response.text}"
            )

    @task
    def save_file(checkpoint_result, data_to_ingest_df) -> None:
        good_data_folder = GOOD_DATA_PATH
        bad_data_folder = BAD_DATA_PATH

        default_file_name = (
            f"default_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv"
        )
        # Attempt to get the file name from DataFrame attributes (or another source)
        file_name = data_to_ingest_df.attrs.get("file_name", default_file_name)

        # Collect all bad row indices from the validation result
        bad_row_indices = set()
        for result in checkpoint_result["run_results"].values():
            for expectation in result["validation_result"]["results"]:
                if "unexpected_index_list" in expectation["result"]:
                    bad_row_indices.update(
                        expectation["result"]["unexpected_index_list"]
                    )

        # Convert bad_row_indices to a sorted list and remove duplicates
        bad_row_indices = sorted(set(bad_row_indices))

        # Split data into good and bad based on bad row indices
        bad_data = data_to_ingest_df.iloc[list(bad_row_indices)]
        good_data = data_to_ingest_df.drop(bad_row_indices)

        try:
            # Save data based on the condition
            if good_data.empty:
                bad_data.to_csv(
                    os.path.join(bad_data_folder, file_name), index=False
                )
                print(
                    f"All rows have issues. Saved to {bad_data_folder}/{file_name}"
                )
            elif bad_data.empty:
                good_data.to_csv(
                    os.path.join(good_data_folder, file_name), index=False
                )
                print(
                    f"All rows are good. Saved to {good_data_folder}/{file_name}"
                )
            else:
                good_data_path = os.path.join(good_data_folder, file_name)
                bad_data_path = os.path.join(
                    bad_data_folder, f"bad_{file_name}"
                )

                good_data.to_csv(good_data_path, index=False)
                bad_data.to_csv(bad_data_path, index=False)

                print(
                    f"Split data into good and bad.\n"
                    f"Good data saved to: {good_data_path}\n"
                    f"Bad data saved to: {bad_data_path}"
                )

        except Exception as e:
            print(f"Error saving files: {e}")

    @task
    def save_statistics(checkpoint_result) -> None:
        return
        # file_name = checkpoint_result['run_id']
        # ingestion_time = datetime.now()

        # total_rows = 0
        # valid_rows = 0
        # invalid_rows = 0
        # missing_values_rows = 0
        # outlier_rows = 0
        # invalid_format_rows = 0
        # missing_features_rows = 0
        # data_drift = False
        # drift_feature = None
        # drift_value = None

        # # Loop through validation results
        # for result in checkpoint_result["run_results"].values():
        #     expectation_suite_name = result["expectation_suite_name"]
        #     statistics = result["statistics"]

        #     total_rows += statistics["evaluated_expectations"]
        #     valid_rows += statistics["successful_expectations"]
        #     invalid_rows += statistics["unsuccessful_expectations"]

        #     # Check for specific errors
        #     for validation_result in result["validation_result"]["results"]:
        #         if "missing" in validation_result["expectation_config"][
        # "expectation_type"].lower():
        #             missing_values_rows += 1
        #         if "outlier" in validation_result["expectation_config"]
        # ["expectation_type"].lower():
        #             outlier_rows += 1
        #         if "invalid_format" in validation_result["expectation_config"]
        # ["expectation_type"].lower():
        #             invalid_format_rows += 1
        #         if "missing_features" in validation_result["expectation_config"]
        # ["expectation_type"].lower():
        #             missing_features_rows += 1

        #     # Data drift (if applicable)
        #     if "data_drift" in result:
        #         data_drift = True
        #         drift_feature = result.get("drift_feature", None)
        #         drift_value = result.get("drift_value", None)

    data_to_ingest_df = read_data()
    checkpoint_result = validate_data(data_to_ingest_df)
    save_file(checkpoint_result, data_to_ingest_df)


ingest_data_dag = ingest_data()
