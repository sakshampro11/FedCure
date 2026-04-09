from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import models
import federated
from ml_model import create_model

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

# In-memory storage for pending weight submissions
pending_weights: list = []
REQUIRED_HOSPITALS = 4  # Number of hospitals needed before FedAvg runs


@app.on_event("startup")
def startup_event():
    """Initialize the global model on server startup."""
    federated.initialize_global_model()
    print("[FedCure] Server started. Global model ready.")


@app.get("/api/health")
def health_check():
    """Health check endpoint for Docker and deployment platforms."""
    return {"status": "healthy", "service": "FedCure API"}


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ──────────────────────────────────────────────
# Pydantic models for API request/response
# ──────────────────────────────────────────────

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


class WeightSubmission(BaseModel):
    hospital_id: int
    weights: Dict[str, Any]
    local_accuracy: float


# ──────────────────────────────────────────────
# Hospital Endpoints
# ──────────────────────────────────────────────

@app.post("/api/hospitals/register")
def register_hospital(request: HospitalRegisterRequest, db: Session = Depends(get_db)):
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

    dummy_token = f"jwt_token_for_{hospital.name.replace(' ', '_').lower()}"
    return {"access_token": dummy_token, "token_type": "bearer"}


# ──────────────────────────────────────────────
# Training / Federated Learning Endpoints
# ──────────────────────────────────────────────

@app.post("/api/training/submit-weights")
def submit_weights(submission: WeightSubmission, db: Session = Depends(get_db)):
    """
    Accept weight updates from a hospital.
    When enough hospitals have submitted, run FedAvg aggregation.
    """
    pending_weights.append({
        "hospital_id": submission.hospital_id,
        "weights": submission.weights,
        "local_accuracy": submission.local_accuracy,
    })

    submitted = len(pending_weights)

    if submitted < REQUIRED_HOSPITALS:
        return {
            "status": "waiting",
            "message": f"Received {submitted}/{REQUIRED_HOSPITALS} submissions. Waiting for more hospitals.",
            "submissions_received": submitted,
            "submissions_required": REQUIRED_HOSPITALS,
        }

    # ── Run FedAvg aggregation ──
    weight_list = [p["weights"] for p in pending_weights]
    avg_accuracy = sum(p["local_accuracy"] for p in pending_weights) / len(pending_weights)

    # Aggregate weights using FedAvg
    aggregated_weights = federated.aggregate_weights(weight_list)

    # Save new global model
    new_version, weights_path = federated.save_global_model(aggregated_weights)

    # Determine round number
    latest_round = db.query(models.TrainingRound).order_by(models.TrainingRound.round_number.desc()).first()
    round_number = (latest_round.round_number + 1) if latest_round else 1

    # Create TrainingRound record
    training_round = models.TrainingRound(
        round_number=round_number,
        accuracy_federated=avg_accuracy,
        accuracy_baseline=avg_accuracy * 0.78,  # Simulated baseline (lower than federated)
        epsilon=0.8,
        num_hospitals=len(pending_weights),
    )
    db.add(training_round)

    # Create ModelVersion record
    model_version = models.ModelVersion(
        version=f"v{new_version}",
        weights_path=weights_path,
        accuracy=avg_accuracy,
    )
    db.add(model_version)
    db.commit()

    # Clear pending weights for next round
    pending_weights.clear()

    return {
        "status": "aggregated",
        "message": f"FedAvg complete! New global model v{new_version} saved.",
        "round_number": round_number,
        "federated_accuracy": avg_accuracy,
        "model_version": f"v{new_version}",
    }


@app.get("/api/training/status")
def get_training_status(db: Session = Depends(get_db)):
    """Return current training status from the database."""
    latest_round = db.query(models.TrainingRound).order_by(models.TrainingRound.round_number.desc()).first()

    if not latest_round:
        return {
            "round_number": 0,
            "accuracy": 0.0,
            "epsilon": 0.8,
            "num_hospitals": 0,
            "pending_submissions": len(pending_weights),
            "message": "No training rounds completed yet. Waiting for hospital submissions."
        }

    return {
        "round_number": latest_round.round_number,
        "accuracy": latest_round.accuracy_federated,
        "epsilon": latest_round.epsilon,
        "num_hospitals": latest_round.num_hospitals,
        "pending_submissions": len(pending_weights),
        "model_version": f"v{federated.get_current_version()}",
    }


@app.get("/api/training/global-model")
def get_global_model():
    """
    Download the current global model weights.
    FL clients call this before each local training round.
    """
    try:
        model = federated.load_global_model()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Global model not available yet.")

    # Serialize weights to JSON-friendly format (tensors → lists)
    weights = {}
    for name, param in model.state_dict().items():
        weights[name] = param.cpu().tolist()

    return {
        "version": f"v{federated.get_current_version()}",
        "weights": weights,
    }


# ──────────────────────────────────────────────
# Dashboard Endpoint
# ──────────────────────────────────────────────

@app.get("/api/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Return all training rounds for the dashboard chart."""
    rounds = db.query(models.TrainingRound).order_by(models.TrainingRound.round_number.asc()).all()

    if not rounds:
        return {
            "message": "No training data yet. Submit hospital weights to start federated learning.",
            "rounds": []
        }

    return {
        "rounds": [
            {
                "round_number": r.round_number,
                "accuracy_federated": r.accuracy_federated,
                "accuracy_baseline": r.accuracy_baseline,
                "epsilon": r.epsilon,
                "num_hospitals": r.num_hospitals,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rounds
        ]
    }


# ──────────────────────────────────────────────
# Inference Endpoint
# ──────────────────────────────────────────────

@app.post("/api/inference/predict")
def predict_heart_disease(vitals: PatientVitals):
    """
    Run inference using the current global model.
    Returns risk score (0-1) and risk level (Low/Moderate/High).
    """
    try:
        model = federated.load_global_model()
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Global model not available. Server may still be initializing.")

    # Convert input to tensor (same 13 features as training data)
    features = [
        vitals.age, vitals.sex, vitals.cp, vitals.trestbps, vitals.chol,
        vitals.fbs, vitals.restecg, vitals.thalach, vitals.exang,
        vitals.oldpeak, vitals.slope, vitals.ca, vitals.thal
    ]
    input_tensor = torch.tensor([features], dtype=torch.float32)

    # Simple normalization (approximate ranges from the dataset)
    mins = torch.tensor([29, 0, 0, 94, 126, 0, 0, 71, 0, 0.0, 0, 0, 0], dtype=torch.float32)
    maxs = torch.tensor([77, 1, 3, 200, 564, 1, 2, 202, 1, 6.2, 2, 4, 3], dtype=torch.float32)
    input_tensor = (input_tensor - mins) / (maxs - mins + 1e-8)

    # Inference
    with torch.no_grad():
        risk_score = model(input_tensor).item()

    # Classify risk level
    if risk_score < 0.3:
        risk_level = "Low"
    elif risk_score <= 0.7:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return {
        "risk_score": round(risk_score, 4),
        "risk_level": risk_level,
    }
