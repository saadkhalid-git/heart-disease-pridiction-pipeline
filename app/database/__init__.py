from __future__ import annotations

import os
import sys
from os.path import abspath
from os.path import dirname

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Path appending
d = dirname(abspath("__file__"))
sys.path.append(d)

# Load environment variables from the .env file
env_path = "config/development.env"
load_dotenv(env_path)

# Database configuration
DB_URL = os.getenv("DB_URL")

# Ensure DB_URL is loaded from environment variables
if not DB_URL:
    raise ValueError("DB_URL is not set in the environment variables.")

# Create the engine and session factory
try:
    engine = create_engine(DB_URL)
    # Test the connection
    with engine.connect() as connection:
        print("Database connection established successfully.")
except Exception as e:
    print(f"Failed to connect to the database: {e}")
    raise

Session = sessionmaker(bind=engine)

# Declarative base for ORM models
Base = declarative_base()
