"""FedCure FastAPI application."""

from __future__ import annotations

import hashlib
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

import torch
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import db_models, federated
from .config import settings
from .database import SessionLocal, engine


JWT_ALGORITHM = "HS256"
api_key_scheme = HTTPBearer(auto_error=False)
aggregation_lock = threading.Lock()

app = FastAPI(
    title="FedCure API",
    version="1.0.0",
    description="Authenticated federated-learning coordination API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


class HospitalRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    location: str = Field(min_length=2, max_length=200)
    admin_email: str = Field(min_length=3, max_length=320)


class HospitalLoginRequest(BaseModel):
    api_key: str = Field(min_length=20, max_length=200)


class PatientVitals(BaseModel):
    age: int = Field(ge=1, le=130)
    sex: int = Field(ge=0, le=1)
    cp: int = Field(ge=0, le=4)
    trestbps: int = Field(ge=40, le=300)
    chol: int = Field(ge=50, le=1000)
    fbs: int = Field(ge=0, le=1)
    restecg: int = Field(ge=0, le=2)
    thalach: int = Field(ge=30, le=300)
    exang: int = Field(ge=0, le=1)
    oldpeak: float = Field(ge=0, le=20)
    slope: int = Field(ge=0, le=2)


class WeightSubmission(BaseModel):
    weights: dict[str, Any]
    local_accuracy: float = Field(ge=0, le=1)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def _create_api_key() -> str:
    return f"fc_{secrets.token_urlsafe(32)}"


def _create_access_token(hospital: db_models.Hospital) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is not configured.")
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_minutes
    )
    return jwt.encode(
        {"sub": str(hospital.id), "type": "access", "exp": expires_at},
        settings.jwt_secret,
        algorithm=JWT_ALGORITHM,
    )


def _credential_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_current_hospital(
    credentials: HTTPAuthorizationCredentials | None = Depends(api_key_scheme),
    db: Session = Depends(get_db),
) -> db_models.Hospital:
    if not credentials or credentials.scheme.lower() != "bearer" or not settings.jwt_secret:
        raise _credential_error()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[JWT_ALGORITHM],
        )
        hospital_id = int(payload.get("sub", ""))
        if payload.get("type") != "access":
            raise ValueError("Invalid token type.")
    except (JWTError, TypeError, ValueError):
        raise _credential_error() from None

    hospital = db.get(db_models.Hospital, hospital_id)
    if not hospital or not hospital.is_active:
        raise _credential_error()
    return hospital


def authenticate_fl_client(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> db_models.Hospital:
    if not x_api_key:
        raise _credential_error()
    hospital = (
        db.query(db_models.Hospital)
        .filter(db_models.Hospital.api_key_hash == _hash_api_key(x_api_key))
        .first()
    )
    if not hospital or not hospital.is_active:
        raise _credential_error()
    return hospital


def _latest_model(db: Session) -> db_models.ModelVersion:
    model = (
        db.query(db_models.ModelVersion)
        .order_by(db_models.ModelVersion.version_number.desc())
        .first()
    )
    if not model:
        raise HTTPException(status_code=503, detail="Global model is initializing.")
    return model


def _next_round_number(db: Session) -> int:
    latest_round = (
        db.query(db_models.TrainingRound)
        .order_by(db_models.TrainingRound.round_number.desc())
        .first()
    )
    return (latest_round.round_number + 1) if latest_round else 1


@app.on_event("startup")
def startup_event() -> None:
    settings.validate_for_startup()
    db_models.Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not _latest_model_or_none(db):
            db.add(
                db_models.ModelVersion(
                    version_number=0,
                    accuracy=None,
                    weights=federated.serialize_state_dict(federated.initial_state_dict()),
                )
            )
            db.commit()


def _latest_model_or_none(db: Session) -> db_models.ModelVersion | None:
    return (
        db.query(db_models.ModelVersion)
        .order_by(db_models.ModelVersion.version_number.desc())
        .first()
    )


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "FedCure API"}


@app.post("/api/hospitals/register", status_code=status.HTTP_201_CREATED)
def register_hospital(
    request: HospitalRegisterRequest,
    x_registration_token: str | None = Header(
        default=None, alias="X-Registration-Token"
    ),
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    if not x_registration_token or not secrets.compare_digest(
        x_registration_token, settings.registration_token or ""
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid network enrollment code.",
        )
    api_key = _create_api_key()
    hospital = db_models.Hospital(
        name=request.name.strip(),
        location=request.location.strip(),
        admin_email=request.admin_email.strip().lower(),
        api_key_hash=_hash_api_key(api_key),
    )
    try:
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this name or administrator email already exists.",
        ) from None

    return {"hospital_id": hospital.id, "api_key": api_key}


@app.post("/api/hospitals/login")
def login_hospital(
    request: HospitalLoginRequest, db: Session = Depends(get_db)
) -> dict[str, str]:
    hospital = (
        db.query(db_models.Hospital)
        .filter(db_models.Hospital.api_key_hash == _hash_api_key(request.api_key))
        .first()
    )
    if not hospital or not hospital.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
    return {
        "access_token": _create_access_token(hospital),
        "token_type": "bearer",
    }


@app.get("/api/training/global-model")
def get_global_model(
    _: db_models.Hospital = Depends(authenticate_fl_client),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    model = _latest_model(db)
    state_dict = federated.deserialize_state_dict(model.weights)
    return {
        "version": f"v{model.version_number}",
        "weights": federated.state_dict_as_json(state_dict),
    }


@app.post("/api/training/submit-weights")
def submit_weights(
    submission: WeightSubmission,
    hospital: db_models.Hospital = Depends(authenticate_fl_client),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        federated.validate_submitted_weights(submission.weights)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    # Render is intentionally configured with one API instance. This lock also protects
    # the aggregate-and-clear transition from concurrent requests in that instance.
    with aggregation_lock:
        round_number = _next_round_number(db)
        pending = (
            db.query(db_models.PendingSubmission)
            .filter(
                db_models.PendingSubmission.round_number == round_number,
                db_models.PendingSubmission.hospital_id == hospital.id,
            )
            .first()
        )
        if pending:
            pending.weights = submission.weights
            pending.local_accuracy = submission.local_accuracy
        else:
            db.add(
                db_models.PendingSubmission(
                    round_number=round_number,
                    hospital_id=hospital.id,
                    weights=submission.weights,
                    local_accuracy=submission.local_accuracy,
                )
            )
        db.flush()

        pending_submissions = (
            db.query(db_models.PendingSubmission)
            .filter(db_models.PendingSubmission.round_number == round_number)
            .order_by(db_models.PendingSubmission.hospital_id.asc())
            .all()
        )
        if len(pending_submissions) < settings.required_hospitals:
            db.commit()
            return {
                "status": "waiting",
                "message": (
                    f"Received updates from {len(pending_submissions)}/"
                    f"{settings.required_hospitals} hospitals."
                ),
                "round_number": round_number,
                "submissions_received": len(pending_submissions),
                "submissions_required": settings.required_hospitals,
            }

        try:
            aggregated_weights = federated.aggregate_weights(
                [item.weights for item in pending_submissions]
            )
            latest_model = _latest_model(db)
            average_accuracy = sum(
                item.local_accuracy for item in pending_submissions
            ) / len(pending_submissions)
            next_version = latest_model.version_number + 1

            db.add(
                db_models.TrainingRound(
                    round_number=round_number,
                    accuracy_federated=average_accuracy,
                    epsilon=0.8,
                    num_hospitals=len(pending_submissions),
                )
            )
            db.add(
                db_models.ModelVersion(
                    version_number=next_version,
                    accuracy=average_accuracy,
                    weights=federated.serialize_state_dict(aggregated_weights),
                )
            )
            (
                db.query(db_models.PendingSubmission)
                .filter(db_models.PendingSubmission.round_number == round_number)
                .delete(synchronize_session=False)
            )
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to aggregate this training round.",
            ) from None

    return {
        "status": "aggregated",
        "message": f"FedAvg completed. Global model v{next_version} is available.",
        "round_number": round_number,
        "federated_accuracy": average_accuracy,
        "model_version": f"v{next_version}",
    }


@app.get("/api/training/status")
def get_training_status(
    _: db_models.Hospital = Depends(require_current_hospital),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    latest_round = (
        db.query(db_models.TrainingRound)
        .order_by(db_models.TrainingRound.round_number.desc())
        .first()
    )
    pending_count = db.query(db_models.PendingSubmission).count()
    latest_model = _latest_model(db)

    if not latest_round:
        return {
            "round_number": 0,
            "accuracy": 0.0,
            "epsilon": 0.8,
            "num_hospitals": 0,
            "pending_submissions": pending_count,
            "model_version": f"v{latest_model.version_number}",
        }
    return {
        "round_number": latest_round.round_number,
        "accuracy": latest_round.accuracy_federated,
        "epsilon": latest_round.epsilon,
        "num_hospitals": latest_round.num_hospitals,
        "pending_submissions": pending_count,
        "model_version": f"v{latest_model.version_number}",
    }


@app.get("/api/dashboard/metrics")
def get_dashboard_metrics(
    _: db_models.Hospital = Depends(require_current_hospital),
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, Any]]]:
    rounds = (
        db.query(db_models.TrainingRound)
        .order_by(db_models.TrainingRound.round_number.asc())
        .all()
    )
    return {
        "rounds": [
            {
                "round_number": item.round_number,
                "accuracy_federated": item.accuracy_federated,
                "epsilon": item.epsilon,
                "num_hospitals": item.num_hospitals,
                "created_at": item.created_at.isoformat(),
            }
            for item in rounds
        ]
    }


@app.post("/api/inference/predict")
def predict_heart_disease(
    vitals: PatientVitals,
    _: db_models.Hospital = Depends(require_current_hospital),
    db: Session = Depends(get_db),
) -> dict[str, float | str]:
    model_record = _latest_model(db)
    model = federated.model_from_state_dict(
        federated.deserialize_state_dict(model_record.weights)
    )
    features = torch.tensor(
        [[
            vitals.age,
            vitals.sex,
            vitals.cp,
            vitals.trestbps,
            vitals.chol,
            vitals.fbs,
            vitals.restecg,
            vitals.thalach,
            vitals.exang,
            vitals.oldpeak,
            vitals.slope,
        ]],
        dtype=torch.float32,
    )
    means = torch.tensor(
        [53.720, 0.764, 3.233, 132.263, 245.063, 0.213, 0.698, 139.733, 0.387, 0.923, 1.624]
    )
    stds = torch.tensor(
        [9.358, 0.425, 0.935, 17.964, 52.930, 0.410, 0.870, 25.518, 0.487, 1.086, 0.610]
    )
    normalized_features = (features - means) / (stds + 1e-8)
    with torch.no_grad():
        risk_score = model(normalized_features).item()

    risk_level = "Low" if risk_score < 0.3 else "Moderate" if risk_score <= 0.7 else "High"
    return {"risk_score": round(risk_score, 4), "risk_level": risk_level}
