from __future__ import annotations

import sys
from os.path import abspath
from os.path import dirname
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pandas as pd
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel


# Path appending
d = dirname(dirname(abspath("__file__")))
sys.path.append(d)

from database.db_service import DBService
from database.models.predictions import Predictions

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
async def get_past_predictions():
    try:
        # Fetch all past predictions from the database
        past_predictions = DBService.where(Predictions)

        return past_predictions

    except Exception as e:
        # Catch and return unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
