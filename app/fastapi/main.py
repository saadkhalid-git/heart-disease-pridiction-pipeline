from __future__ import annotations

import sys
from datetime import datetime
from os.path import abspath
from os.path import dirname
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pandas as pd
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import and_


# Path appending
d = dirname(dirname(abspath("__file__")))
sys.path.append(d)

from database.db_service import DBService
from database.models.predictions import Predictions
from database.connection_service import get_db_connection as database

from ml_models.predictor import Predictor

app = FastAPI()


class PatientData(BaseModel):
    age: int
    gender: str
    chest_pain_type: str
    resting_bp: int
    cholesterol: int
    fasting_bs: int
    resting_ecg: str
    max_hr: int
    exercise_angina: str
    old_peak: float
    st_slope: str


data_store: list[PatientData] = []
predictor = Predictor()


def add_date_filter(filters, date_value, comparison, field_name):
    """Helper function to parse date and add filter."""
    try:
        date = datetime.fromisoformat(date_value)
        filters.append(comparison(field_name, date))
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD."
        )


def convert_patient_data_to_dataframe(patient_data_list):
    # Ensure the list is not empty
    if not patient_data_list:
        return pd.DataFrame()

    # Convert list of PatientData objects to list of dictionaries
    data_dicts = [vars(patient) for patient in patient_data_list]

    # Create DataFrame from list of dictionaries
    df = pd.DataFrame(data_dicts)
    return df


@app.post("/predict")
def predict(data: list[PatientData]):
    try:
        patient_data_list = [PatientData(**item.dict()) for item in data]
        df = convert_patient_data_to_dataframe(patient_data_list)

        if df.empty:
            raise HTTPException(status_code=400, detail="Empty data provided")

        res = predictor.predict(df)

        df["heart_disease"] = res["prediction"]
        predictions = df.to_dict(orient="records")
        DBService.add_multiple(Predictions, predictions)
        return predictions

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/past-predictions")
async def get_past_predictions(
    search_text: str | None = None,
    column: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int | None = 1,
    page_size: int | None = 10,
):
    filters = []

    # Add date filters if provided
    if start_date:
        add_date_filter(
            filters,
            start_date,
            lambda field, date: Predictions.created_at >= date,
            Predictions.created_at,
        )

    if end_date:
        add_date_filter(
            filters,
            end_date,
            lambda field, date: Predictions.created_at <= date,
            Predictions.created_at,
        )

    # Add column and search text filter if provided
    if column and search_text:
        if hasattr(Predictions, column):
            filters.append(getattr(Predictions, column) == search_text)
        else:
            raise HTTPException(
                status_code=400, detail=f"Column '{column}' does not exist."
            )

    # Fetch filtered past predictions from the database with pagination
    past_predictions = DBService.where(
        Predictions, filters, page=page, page_size=page_size
    )

    # Format created_at to string for the response
    for prediction in past_predictions:
        prediction.created_at = prediction.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return past_predictions
