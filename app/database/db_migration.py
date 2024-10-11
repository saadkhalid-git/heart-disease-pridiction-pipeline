from __future__ import annotations

from sqlalchemy import inspect

from . import Base
from . import engine
from app.database.models.error_stats import ErrorStats
from app.database.models.predictions import Predictions


# Check if table exists
def table_exists(engine, table_name: str) -> bool:
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


# Create table if it doesn't exist
def create_table_if_not_exists(engine, model, table_name: str):
    if not table_exists(engine, table_name):
        model.__table__.create(engine)
        print(f"Table '{table_name}' created successfully.")
    else:
        print(f"Table '{table_name}' already exists.")


# Create tables
create_table_if_not_exists(engine, Predictions, "predictions")
create_table_if_not_exists(engine, ErrorStats, "error_stats")
