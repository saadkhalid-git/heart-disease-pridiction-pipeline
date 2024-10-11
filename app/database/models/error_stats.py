from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.sql import func

from .. import Base


class ErrorStats(Base):
    __tablename__ = "error_stats"

    # Define columns with snake case names
    id = Column(Integer, primary_key=True)
    run_id = Column(String)
    criticality = Column(String)
    report_link = Column(String)
    total_rows = Column(Integer)
    failed_rows = Column(String)
    evaluated_expectations = Column(String)
    unsuccessful_expectations = Column(String)
    successful_expectations = Column(String)
    error_details = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )
