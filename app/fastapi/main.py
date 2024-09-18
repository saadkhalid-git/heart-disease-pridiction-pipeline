from __future__ import annotations

import sys
from os.path import abspath
from os.path import dirname

from fastapi import FastAPI
from fastapi import HTTPException

# Path appending
d = dirname(dirname(abspath("__file__")))
sys.path.append(d)

from database.prediction_service import PredictionService
from database.models.predictions import Predictions

app = FastAPI()


@app.get("/")
def read_root():
    return "Welcome to Heart Disease Prediction API"


@app.post("/predict")
def predict():
    return "Welcome to Heart Disease Prediction API"


@app.get("/past-predictions")
async def get_past_predictions():
    # Fetch all past predictions from the database using the Prediction class
    past_predictions = PredictionService.where(Predictions)

    if not past_predictions:
        raise HTTPException(
            status_code=404, detail="No past predictions found"
        )

    # Process database rows into response format
    # response = []
    response = past_predictions
    return response
