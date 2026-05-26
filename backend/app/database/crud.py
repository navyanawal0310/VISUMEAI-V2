"""
app/database/crud.py
--------------------
Create and read operations for CandidateRecord.
"""

from typing import List
from sqlalchemy.orm import Session
from .models import CandidateRecord


def save_evaluation(
    db: Session,
    *,
    candidate_name: str,
    resume_filename: str,
    job_title: str,
    overall_score: float,
    technical_score: float,
    experience_score: float,
    ats_score: float,
    communication_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
    report_url: str | None,
) -> CandidateRecord:
    """Insert a new evaluation row and return the persisted record."""
    record = CandidateRecord(
        candidate_name=candidate_name,
        resume_filename=resume_filename,
        job_title=job_title,
        overall_score=overall_score,
        technical_score=technical_score,
        experience_score=experience_score,
        ats_score=ats_score,
        communication_score=communication_score,
        matched_skills=", ".join(matched_skills),
        missing_skills=", ".join(missing_skills),
        report_url=report_url,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all_evaluations(db: Session) -> List[CandidateRecord]:
    """Return all evaluations, newest first."""
    return (
        db.query(CandidateRecord)
        .order_by(CandidateRecord.created_at.desc())
        .all()
    )