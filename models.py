from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Hospital(Base):
    __tablename__ = "hospitals"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    admin_email = Column(String, index=True)
    api_key = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class TrainingRound(Base):
    __tablename__ = "training_rounds"
    id = Column(Integer, primary_key=True, index=True)
    round_number = Column(Integer, unique=True, index=True)
    accuracy_federated = Column(Float)
    accuracy_baseline = Column(Float)
    epsilon = Column(Float)
    num_hospitals = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True)
    weights_path = Column(String)
    accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
