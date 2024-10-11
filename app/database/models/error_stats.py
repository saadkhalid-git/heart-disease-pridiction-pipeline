from __future__ import annotations

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func

from .. import Base


class ErrorStats(Base):
    __tablename__ = "error_stats"

    # Define columns with snake case names
    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    gender = Column(String)
    chest_pain_type = Column(String)
    resting_bp = Column(Integer)
    cholesterol = Column(Integer)
    fasting_bs = Column(Integer)
    resting_ecg = Column(String)
    max_hr = Column(Integer)
    exercise_angina = Column(String)
    old_peak = Column(Float)
    st_slope = Column(String)
    heart_disease = Column(Integer)

    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
