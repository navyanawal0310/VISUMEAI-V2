"""
app/database/db.py
------------------
SQLite engine and session factory.
The database file is created beside the uploads/ directory.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Place visume.db next to the uploads directory so it survives container restarts
_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "visume.db")
DATABASE_URL = f"sqlite:///{os.path.normpath(_DB_PATH)}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()