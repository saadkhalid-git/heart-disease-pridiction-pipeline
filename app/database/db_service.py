from __future__ import annotations

from sqlalchemy import and_
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from . import Session


class DBService:
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
    def where(model_class, filters=None, page=1, page_size=10):
        session = Session()
        try:
            query = session.query(model_class)

            if filters:
                # Apply all filter conditions combined with AND
                query = query.filter(and_(*filters))

            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)

            results = query.all()
            return results

        finally:
            session.close()

    @staticmethod
    def add_multiple(model, data):
        session = Session()
        try:
            # Assuming the model has a table name attribute
            table_name = model.__tablename__

            # Construct the SQL query
            keys = data[0].keys()
            columns = ", ".join(keys)
            values_placeholder = ", ".join([f":{key}" for key in keys])
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values_placeholder})"

            # Prepare parameters for the query
            params = [dict(item) for item in data]

            # Execute the raw query for each dictionary in the list
            with session.begin():
                print(text(sql), params)
                session.execute(text(sql), params)
                return True

        except SQLAlchemyError as e:
            # Rollback in case of a database error
            session.rollback()
            raise RuntimeError("Database error: " + str(e))
        except Exception as e:
            # Rollback for other errors
            session.rollback()
            raise RuntimeError("Unexpected error: " + str(e))
        finally:
            # Ensure the session is closed
            session.close()
