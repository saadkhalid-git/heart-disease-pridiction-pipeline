from __future__ import annotations

from . import Session


class PredictionService:
    @staticmethod
    def add(model, **kwargs):
        session = Session()
        try:
            new_data = model(**kwargs)
            session.add(new_data)
            session.commit()
        finally:
            session.close()

    @staticmethod
    def where(model_class, **kwargs):
        session = Session()
        try:
            query = session.query(model_class).filter_by(**kwargs)
            results = query.all()
            return results
        finally:
            session.close()


# # Example usage
# if __name__ == "__main__":
#     # Add a prediction
#     PredictionService.add(Prediction, model='example_model')

#     # Query predictions
#     results = PredictionService.where(Prediction, model='example_model')
#     print(results)
