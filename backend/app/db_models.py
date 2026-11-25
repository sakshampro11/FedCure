"""SQLAlchemy persistence models."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    location = Column(String(200), nullable=False)
    admin_email = Column(String(320), unique=True, nullable=False, index=True)
    api_key_hash = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class TrainingRound(Base):
    __tablename__ = "training_rounds"

    id = Column(Integer, primary_key=True)
    round_number = Column(Integer, unique=True, nullable=False, index=True)
    accuracy_federated = Column(Float, nullable=False)
    epsilon = Column(Float, nullable=False)
    num_hospitals = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True)
    version_number = Column(Integer, unique=True, nullable=False, index=True)
    accuracy = Column(Float, nullable=True)
    weights = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PendingSubmission(Base):
    __tablename__ = "pending_submissions"
    __table_args__ = (
        UniqueConstraint("round_number", "hospital_id", name="uq_round_hospital_submission"),
    )

    id = Column(Integer, primary_key=True)
    round_number = Column(Integer, nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    weights = Column(JSON, nullable=False)
    local_accuracy = Column(Float, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
