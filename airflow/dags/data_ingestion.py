from __future__ import annotations

import http.client
import json
import logging
import os
import random
import sys
from datetime import datetime
from datetime import timedelta
from os.path import abspath
from os.path import dirname
from urllib.parse import urlparse

import great_expectations as gx
import pandas as pd
import requests
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.data_context import DataContext

from airflow.decorators import dag
from airflow.decorators import task
from airflow.exceptions import AirflowFailException
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.utils.dates import days_ago

# Path appending
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)


# Import the DBService and ErrorStats model
from app.database.db_service import DBService
from app.database.models.error_stats import ErrorStats


# Define environment variables for paths
RAW_DATA_PATH = os.getenv("RAW_DATA_PATH") or "data/raw_data"
GOOD_DATA_PATH = os.getenv("GOOD_DATA_PATH") or "data/good_data"
BAD_DATA_PATH = os.getenv("BAD_DATA_PATH") or "data/bad_data"

# Create directories if they don't exist
os.makedirs(GOOD_DATA_PATH, exist_ok=True)
os.makedirs(BAD_DATA_PATH, exist_ok=True)
os.makedirs(RAW_DATA_PATH, exist_ok=True)

# Define environment variables for configuration
PROCESSED_FILES_KEY = os.getenv("PROCESSED_FILES_KEY") or "process_files"
API_URL = os.getenv("API_URL") or "http://localhost:8000/"

WEBHOOK_URL = (
    "https://epitafr.webhook.office.com/webhookb2/a75c8ce0-9d6b-439b-8658-"
    "cfeb1f119679@3534b3d7-316c-4bc9-9ede-605c860f49d2/IncomingWebhook/"
    "d3a450064aba4749b9954dc984f21b30/34cf83e2-d429-4e20-9ca2-d0ac2c22a0a2/"
    "V2RfyAvESI2_e91ROEKSws4ebKcgD9uD5YTBpQ6gBAO_g1"
)

# great_expectations configuration
ge_directory = os.getenv("GE_DIRECTORY") or "gx"
ge_directory = os.path.abspath(ge_directory)
context = gx.get_context(context_root_dir=ge_directory)
expectation_suite_name = "heart_disease_validation_suite"


@dag(
    dag_id="data_ingestion_dag",
    description="Ingest data from a file to another DAG",
    tags=["dsp", "data_ingestion"],
    schedule=timedelta(minutes=5),
    start_date=days_ago(0),  # sets the starting point of the DAG
    max_active_runs=1,  # Ensure only one active run at a time
)
def ingest_data():
    @task(execution_timeout=timedelta(minutes=30))
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
            try:
                selected_file = random.choice(files)
                file_path = os.path.join(RAW_DATA_PATH, selected_file)
                logging.info(f"Selected file: {file_path}")

                data_to_ingest_df = pd.read_csv(file_path)
                data_to_ingest_df.attrs["file_name"] = selected_file

                os.remove(file_path)

                logging.info(
                    f"File {file_path} has been deleted after ingestion."
                )

                return data_to_ingest_df
            except Exception as e:
                raise AirflowFailException(f"Error reading file: {e}")

    @task(execution_timeout=timedelta(minutes=30), multiple_outputs=True)
    def validate_data(data_to_ingest_df: pd.DataFrame):
        try:
            # run_id = data_to_ingest_df.attrs.get("file_name", "default_file_name")
            # run_id = run_id.replace(".csv", "")
            # run_id = run_id + datetime.now()
            # .strftime("%d-%m-%Y %H:%M:%S").replace(" ", "_")
            runtime_request = RuntimeBatchRequest(
                datasource_name="my_datasource",
                data_connector_name="default_runtime_data_connector_name",
                data_asset_name="my_runtime_asset_name",
                runtime_parameters={"batch_data": data_to_ingest_df},
                batch_identifiers={"default_identifier_name": "my_data"},
            )
            validator = context.get_validator(
                batch_request=runtime_request,
                expectation_suite_name=expectation_suite_name,
            )
            checkpoint_result = context.run_checkpoint(
                checkpoint_name="validation_checkpoint", validator=validator
            )

            logging.info(f"Checkpoint Result: {checkpoint_result}")

            return {
                "checkpoint_result": checkpoint_result.to_json_dict(),
                "data_to_ingest": data_to_ingest_df,
            }
        except Exception as e:
            raise AirflowFailException(f"Error validating data: {e}")

    @task(execution_timeout=timedelta(minutes=30))
    def send_alerts(checkpoint_result: dict, webhook_url: str) -> None:
        # Extract relevant statistics and meta information from the result
        results = list(checkpoint_result["run_results"].keys())[0]
        run_indetifier = checkpoint_result["run_results"][results]
        validation_result = run_indetifier["validation_result"]
        stats = validation_result["statistics"]
        data_docs = run_indetifier["actions_results"]["update_data_docs"]

        evaluated_expectations = stats.get("evaluated_expectations", 0)
        successful_expectations = stats.get("successful_expectations", 0)
        unsuccessful_expectations = stats.get("unsuccessful_expectations", 0)

        if unsuccessful_expectations == 1:
            criticality = "low"
        elif unsuccessful_expectations <= 2:
            criticality = "medium"
        else:
            criticality = "high"

        print("results ->", data_docs["local_site"])
        report_link = data_docs.get("local_site", "N/A")

        # Build the alert message
        alert_message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0076D7",
            "summary": "Data Problem Alert",
            "sections": [
                {
                    "activityTitle": "Data Problem Alert",
                    "activitySubtitle": "On heart disease pipeline",
                    "activityImage": (
                        "https://cdn-icons-png.flaticon.com/512/8730/8730487.png"
                    ),
                    "facts": [
                        {"name": "Criticality", "value": criticality},
                        {
                            "name": "Evaluated Expectations:",
                            "value": str(evaluated_expectations),
                        },
                        {
                            "name": "Unsuccessful Expectations:",
                            "value": str(unsuccessful_expectations),
                        },
                        {
                            "name": "Successful Expectations:",
                            "value": str(successful_expectations),
                        },
                        {"name": "Link to Report", "value": report_link},
                    ],
                    "markdown": True,
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Full Report",
                    "targets": [
                        {
                            "os": "default",
                            "uri": report_link,
                        }
                    ],
                }
            ],
        }
        print("alert_message ->", alert_message)

        # Send alert to the teams channel using a webhook

        try:
            # Parse the URL into its components
            parsed_url = urlparse(webhook_url)
            host = parsed_url.netloc
            path = parsed_url.path

            # Establish HTTPS connection
            conn = http.client.HTTPSConnection(host)

            # Convert the message to JSON
            headers = {"Content-type": "application/json"}
            json_data = json.dumps(alert_message)

            # Send the POST request
            conn.request("POST", path, body=json_data, headers=headers)

            # Get the response
            response = conn.getresponse()

            if response.status == 200:
                print("Alert sent to Teams successfully.")
            else:
                print(
                    f"Failed to send alert to Teams. Status code: {response.status}"
                )

            # Close the connection
            conn.close()

        except Exception as e:
            print(f"Error sending alert to Teams: {e}")

    @task(execution_timeout=timedelta(minutes=30))
    def save_file(checkpoint_result, data_to_ingest_df) -> None:
        good_data_folder = GOOD_DATA_PATH
        bad_data_folder = BAD_DATA_PATH

        default_file_name = (
            f"default_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.csv"
        )

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
        files = Variable.get(
            PROCESSED_FILES_KEY, default_var=[], deserialize_json=True
        )
        if not good_data.empty:
            files.append(file_name)
            Variable.set(PROCESSED_FILES_KEY, files, serialize_json=True)

        try:
            # Save data based on the condition
            if good_data.empty:
                bad_data.to_csv(
                    os.path.join(bad_data_folder, file_name), index=False
                )
                logging.info(
                    f"All rows have issues. Saved to {bad_data_folder}/{file_name}"
                )
            elif bad_data.empty:
                good_data.to_csv(
                    os.path.join(good_data_folder, file_name), index=False
                )
                logging.info(
                    f"All rows are good. Saved to {good_data_folder}/{file_name}"
                )
            else:
                good_data_path = os.path.join(good_data_folder, file_name)
                bad_data_path = os.path.join(
                    bad_data_folder, f"bad_{file_name}"
                )

                good_data.to_csv(good_data_path, index=False)
                bad_data.to_csv(bad_data_path, index=False)

                logging.info(
                    f"Split data into good and bad.\n"
                    f"Good data saved to: {good_data_path}\n"
                    f"Bad data saved to: {bad_data_path}"
                )

        except Exception as e:
            raise AirflowFailException(f"Error saving files: {e}")

    @task
    def save_statistics(checkpoint_result: dict) -> None:
        try:
            identifier = list(checkpoint_result["run_results"].keys())[0]
            run_identifier = checkpoint_result["run_results"][identifier]
            validation_result = run_identifier["validation_result"]

            # Extract statistics and data docs
            stats = validation_result["statistics"]
            data_docs = run_identifier["actions_results"]["update_data_docs"]

            # Initialize error details list
            error_details = []

            # Extracting statistics with defaults
            evaluated_expectations = stats.get("evaluated_expectations", 0)
            successful_expectations = stats.get("successful_expectations", 0)
            unsuccessful_expectations = stats.get(
                "unsuccessful_expectations", 0
            )

            if unsuccessful_expectations == 1:
                criticality = "low"
            elif unsuccessful_expectations <= 2:
                criticality = "medium"
            else:
                criticality = "high"

            report_link = data_docs.get("local_site", "N/A")

            # Loop through the expectations and gather error details for failed ones
            expectation_results = validation_result["results"]
            for index, expectation in enumerate(expectation_results):
                if not expectation["success"]:
                    error_details.append(
                        {
                            "expectation_number": index + 1,
                            "column": expectation["expectation_config"][
                                "kwargs"
                            ].get("column", "N/A"),
                            "expectation_type": expectation[
                                "expectation_config"
                            ].get("expectation_type", "N/A"),
                            "unexpected_count": expectation["result"].get(
                                "unexpected_count", "N/A"
                            ),
                            "unexpected_values": expectation["result"].get(
                                "unexpected_list", []
                            ),
                        }
                    )

            # error_stats object to insert into the database,
            error_stats = {
                "run_id": identifier,
                "criticality": criticality,
                "report_link": report_link,
                "total_rows": stats.get("evaluated_row_count", 0),
                "failed_rows": stats.get("failed_row_count", 0),
                "evaluated_expectations": evaluated_expectations,
                "unsuccessful_expectations": unsuccessful_expectations,
                "successful_expectations": successful_expectations,
                "error_details": json.dumps(error_details),
                "updated_at": datetime.now(),
                "created_at": datetime.now(),
            }

            print("error_stats ->", error_stats)

            DBService.add_multiple(ErrorStats, [error_stats])

        except KeyError as e:
            print(f"KeyError: Missing key {str(e)} in checkpoint result.")
            # Optionally, log the error or raise a custom exception
        except TypeError as e:
            print(f"TypeError: {str(e)} - Encountered issue with data types.")
            # Optionally, log the error or raise a custom exception
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            # Optionally, log the error or raise a custom exception

    data_to_ingest_df = read_data()
    data = validate_data(data_to_ingest_df)
    save_file(data["checkpoint_result"], data["data_to_ingest"])
    send_alerts(data["checkpoint_result"], WEBHOOK_URL)
    save_statistics(data["checkpoint_result"])


ingest_data_dag = ingest_data()
