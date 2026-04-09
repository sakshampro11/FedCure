from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import models

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./fedcure.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FedCure API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for API
class HospitalRegisterRequest(BaseModel):
    name: str
    location: str
    admin_email: str


class HospitalLoginRequest(BaseModel):
    api_key: str


class PatientVitals(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int


# API Endpoints

@app.post("/api/hospitals/register")
def register_hospital(request: HospitalRegisterRequest, db: Session = Depends(get_db)):
    # Create new hospital
    new_hospital = models.Hospital(
        name=request.name,
        location=request.location,
        admin_email=request.admin_email
    )
    db.add(new_hospital)
    db.commit()
    db.refresh(new_hospital)

    return {
        "hospital_id": new_hospital.id,
        "api_key": new_hospital.api_key
    }


@app.post("/api/hospitals/login")
def login_hospital(request: HospitalLoginRequest, db: Session = Depends(get_db)):
    hospital = db.query(models.Hospital).filter(models.Hospital.api_key == request.api_key).first()
    if not hospital:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Normally we would encode a proper JWT here, returning a dummy token for hackathon setup
    dummy_token = f"jwt_token_for_{hospital.name.replace(' ', '_').lower()}"
    return {"access_token": dummy_token, "token_type": "bearer"}


@app.get("/api/training/status")
def get_training_status():
    # Placeholder
    return {
        "round_number": 5,
        "accuracy": 0.88,
        "epsilon": 1.2,
        "num_hospitals": 3
    }


@app.get("/api/dashboard/metrics")
def get_dashboard_metrics():
    # Placeholder
    return [
        {"round_number": 1, "accuracy_federated": 0.55, "accuracy_baseline": 0.53},
        {"round_number": 2, "accuracy_federated": 0.65, "accuracy_baseline": 0.58},
        {"round_number": 3, "accuracy_federated": 0.76, "accuracy_baseline": 0.61},
        {"round_number": 4, "accuracy_federated": 0.82, "accuracy_baseline": 0.65},
        {"round_number": 5, "accuracy_federated": 0.88, "accuracy_baseline": 0.68},
    ]


@app.post("/api/inference/predict")
def predict_heart_disease(vitals: PatientVitals):
    # Placeholder logic
    risk_score = 0.75 if vitals.age > 50 and vitals.chol > 200 else 0.25
    risk_level = "High" if risk_score > 0.5 else "Low"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level
    }
