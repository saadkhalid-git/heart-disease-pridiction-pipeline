from __future__ import annotations

from . import engine

# Global variable to store the database connection
db_connection = None


def get_db_connection():
    global db_connection

    if db_connection is not None:
        return db_connection

    db_connection = engine.connect()
    return db_connection


def execute_query(query):
    connection = get_db_connection()
    results = connection.execute(query)
    return results
