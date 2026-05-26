"""
app/database/models.py
----------------------
ORM table definition for candidate evaluations.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from .db import Base


class CandidateRecord(Base):
    __tablename__ = "candidate_evaluations"

    id                  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_name      = Column(String(255), nullable=False, default="Candidate")
    resume_filename     = Column(String(512), nullable=False)
    job_title           = Column(String(255), nullable=False, default="Open Position")

    # Scores (0–100)
    overall_score       = Column(Float, nullable=False, default=0.0)
    technical_score     = Column(Float, nullable=False, default=0.0)
    experience_score    = Column(Float, nullable=False, default=0.0)
    ats_score           = Column(Float, nullable=False, default=0.0)
    communication_score = Column(Float, nullable=False, default=0.0)

    # Skill lists stored as comma-separated strings (simple, no extra tables needed)
    matched_skills      = Column(Text, nullable=False, default="")
    missing_skills      = Column(Text, nullable=False, default="")

    report_url          = Column(String(512), nullable=True)
    created_at          = Column(DateTime, nullable=False, default=datetime.utcnow)