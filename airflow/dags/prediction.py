from __future__ import annotations

import http.client
import json
import logging
import os
import subprocess
from datetime import datetime
from datetime import timedelta
from urllib.parse import urlparse

import pandas as pd

from airflow.decorators import dag
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from airflow.utils.dates import days_ago

GOOD_DATA_PATH = os.getenv("GOOD_DATA_PATH") or "data/good_data"
PROCESSED_FILES_KEY = os.getenv("PROCESSED_FILES_KEY") or "process_files"
API_URL = os.getenv("API_URL") or "http://localhost:8000/"


def map_and_rename_columns(df):
    # Define the mapping of old column names to new column names
    column_mapping = {
        "Gender": "gender",
        "ChestPainType": "chest_pain_type",
        "RestingECG": "resting_ecg",
        "ExerciseAngina": "exercise_angina",
        "Cholesterol": "cholesterol",
        "RestingBP": "resting_bp",
        "MaxHR": "max_hr",
        "Oldpeak": "old_peak",
        "ST_Slope": "st_slope",
        "FastingBS": "fasting_bs",
        "Age": "age",
    }
    desired_order = [
        "age",
        "gender",
        "chest_pain_type",
        "resting_bp",
        "cholesterol",
        "fasting_bs",
        "resting_ecg",
        "max_hr",
        "exercise_angina",
        "old_peak",
        "st_slope",
    ]
    # Rename the columns
    df.rename(columns=column_mapping, inplace=True)
    df = df[list(column_mapping.values())]
    df = df[desired_order]
    # Return the modified DataFrame
    return df


@dag(
    dag_id="prediction",
    description="Check the file and predict",
    tags=["dsp", "prediction"],
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(0),
    max_active_runs=1,
)
def check_and_predict():
    @task
    def check_for_new_data() -> list[str]:
        processed_files = Variable.get(
            PROCESSED_FILES_KEY, default_var=[], deserialize_json=True
        )
        if len(processed_files) == 0:
            raise AirflowSkipException(
                "No new CSV files found to predict, skipping task."
            )

        current_files = [
            file
            for file in os.listdir(GOOD_DATA_PATH)
            if file.endswith(".csv")
        ]
        # Determine new files (not yet processed)
        new_files = [file for file in current_files if file in processed_files]

        logging.info(f"New files detected: {new_files}")
        return new_files

    @task
    def make_prediction(files: list[str]) -> list[str]:
        for file in files:
            file_path = os.path.join(GOOD_DATA_PATH, file)
            df = pd.read_csv(file_path)
            df = map_and_rename_columns(df)
            data = df.to_dict(orient="records")

            # Convert the data to JSON
            json_data = json.dumps(data)

            curl_command = [
                "curl",
                "-X",
                "POST",
                API_URL + "predict",  # URL for the API
                "-H",
                "Content-Type: application/json",  # Set the headers
                "-d",
                json_data,  # Send the JSON data
            ]
            result = subprocess.run(
                curl_command, capture_output=True, text=True
            )

            if result.returncode == 0:
                print("Curl request successful.")
                print("Response:", result.stdout)
            else:
                print("Curl request failed.")
                print("Error:", result.stderr)

        Variable.set(PROCESSED_FILES_KEY, json.dumps([]))

    # Task execution
    new_files_to_predict = check_for_new_data()
    make_prediction(new_files_to_predict)


# Instantiate the DAG
check_and_predict = check_and_predict()
