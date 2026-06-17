import sys
import os

# Ensure the server directory is in sys.path so modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch

import db_models
import federated
from nn_model import create_model
import os

# Load environment variables from .env file
for path in [".env", "../.env", "../../.env"]:
    if os.path.exists(path):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
        break

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fedcure.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FedCure API")

# CORS middleware
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")] if allowed_origins_str else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for pending weight submissions
pending_weights: list = []
pending_hospital_ids: set = set()  # Track unique hospitals that have submitted
REQUIRED_HOSPITALS = 4  # Number of unique hospitals needed before FedAvg runs


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


class WeightSubmission(BaseModel):
    hospital_id: int
    weights: Dict[str, Any]
    local_accuracy: float


# ──────────────────────────────────────────────
# Hospital Endpoints
# ──────────────────────────────────────────────

@app.post("/api/hospitals/register")
def register_hospital(request: HospitalRegisterRequest, db: Session = Depends(get_db)):
    new_hospital = db_models.Hospital(
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
    hospital = db.query(db_models.Hospital).filter(db_models.Hospital.api_key == request.api_key).first()
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
    pending_hospital_ids.add(submission.hospital_id)

    unique_hospitals = len(pending_hospital_ids)

    if unique_hospitals < REQUIRED_HOSPITALS:
        return {
            "status": "waiting",
            "message": f"Received submissions from {unique_hospitals}/{REQUIRED_HOSPITALS} unique hospitals. Waiting for more hospitals.",
            "submissions_received": len(pending_weights),
            "unique_hospitals": unique_hospitals,
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
    latest_round = db.query(db_models.TrainingRound).order_by(db_models.TrainingRound.round_number.desc()).first()
    round_number = (latest_round.round_number + 1) if latest_round else 1

    # Create TrainingRound record
    training_round = db_models.TrainingRound(
        round_number=round_number,
        accuracy_federated=avg_accuracy,
        epsilon=0.8,
        num_hospitals=unique_hospitals,
    )
    db.add(training_round)

    # Create ModelVersion record
    model_version = db_models.ModelVersion(
        version=f"v{new_version}",
        weights_path=weights_path,
        accuracy=avg_accuracy,
    )
    db.add(model_version)
    db.commit()

    # Clear pending weights for next round
    pending_weights.clear()
    pending_hospital_ids.clear()

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
    latest_round = db.query(db_models.TrainingRound).order_by(db_models.TrainingRound.round_number.desc()).first()

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
        
        # Serialize weights to JSON-friendly format (tensors → lists)
        weights = {}
        for name, param in model.state_dict().items():
            weights[name] = param.cpu().tolist()

        return {
            "version": f"v{federated.get_current_version()}",
            "weights": weights,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Global model not available yet.")
    except Exception as e:
        print(f"[ERROR] Failed to load/serialize global model: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing global model: {str(e)}. This might be a version mismatch. Try restarting the server."
        )


# ──────────────────────────────────────────────
# Dashboard Endpoint
# ──────────────────────────────────────────────

@app.get("/api/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Return all training rounds for the dashboard chart."""
    rounds = db.query(db_models.TrainingRound).order_by(db_models.TrainingRound.round_number.asc()).all()

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

    # Convert input to tensor (same 11 features as training data)
    features = [
        vitals.age, vitals.sex, vitals.cp, vitals.trestbps, vitals.chol,
        vitals.fbs, vitals.restecg, vitals.thalach, vitals.exang,
        vitals.oldpeak, vitals.slope
    ]
    input_tensor = torch.tensor([features], dtype=torch.float32)

    # Standard scaling based on the dataset's exact mean and std (matching training setup)
    # These values are computed by temp_scripts/prepare_dataset.py on the ~1190-sample combined dataset
    means = torch.tensor([53.720, 0.764, 3.233, 132.263, 245.063, 0.213, 0.698, 139.733, 0.387, 0.923, 1.624], dtype=torch.float32)
    stds = torch.tensor([9.358, 0.425, 0.935, 17.964, 52.930, 0.410, 0.870, 25.518, 0.487, 1.086, 0.610], dtype=torch.float32)
    input_tensor = (input_tensor - means) / (stds + 1e-8)

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
