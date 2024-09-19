from __future__ import annotations

import numpy as np
import pandas as pd
from joblib import load
from sqlalchemy.orm import Session

# from your_database_model import PredictionData


class Predictor:
    def __init__(self):
        # Load the trained model, encoder, and scaler using static paths
        self.model = load("../ml_models/models/Random_Forest.joblib")
        self.ordinal_encoder = load(
            "../ml_models/models/Ordinal_Encoder.joblib"
        )
        self.scaler = load("../ml_models/models/Standard_Scaler.joblib")
        self.categorical_columns = load(
            "../ml_models/models/categorical_columns.joblib"
        )

    def preprocess(self, df):
        # Handle categorical columns with OrdinalEncoder
        df[self.categorical_columns] = self.ordinal_encoder.transform(
            df[self.categorical_columns]
        )

        # Scale continuous columns with StandardScaler
        df = self.scaler.transform(df)

        return df

    def predict(self, df):
        # Preprocess the DataFrame
        numpy_array = self.preprocess(df)
        try:
            prediction = self.model.predict(numpy_array)
            return {"prediction": prediction.tolist(), "status": 200}
        except Exception as e:
            return {
                "err": "Error during test prediction:" + str(e),
                "status": 400,
            }
