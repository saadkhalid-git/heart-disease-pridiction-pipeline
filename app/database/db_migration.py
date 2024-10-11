from __future__ import annotations

from sqlalchemy import inspect

from . import Base
from . import engine


# Check if table exists
def table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


# Create all tables in the database if they do not exist
if not table_exists(engine, "Predictions"):
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
else:
    print("Table 'Predictions' already exists.")

if not table_exists(engine, "ErrorStats"):
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
else:
    print("Table 'ErrorStats' already exists.")
