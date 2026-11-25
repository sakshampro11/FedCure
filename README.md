# FedCure

FedCure is a federated-learning demonstration for heart-disease risk prediction. Hospitals train locally and submit model updates; the API aggregates those updates into a shared model without receiving the source CSV files.

> This is an engineering demonstration, not a clinical decision-support system. Do not use it for patient diagnosis, treatment, or emergency care.

## Deployment architecture

- Frontend: Next.js on Vercel
- API: FastAPI in Docker on Render
- State: Render Postgres for hospitals, training rounds, pending updates, and compact model checkpoints
- Hospital node: a Docker client that runs beside the hospital's private CSV

The deployment instructions are in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Repository layout

    FedCure/
    ├── backend/
    │   ├── app/                 # FastAPI application, auth, FedAvg, and persistence
    │   ├── Dockerfile           # Render API image
    │   ├── requirements.txt
    │   └── .env.example
    ├── client/                  # Hospital-side training client
    ├── frontend/                # Next.js application deployed to Vercel
    ├── docs/
    │   └── DEPLOYMENT.md
    ├── scripts/                 # Local-only dataset preparation utility
    ├── data/                    # Local-only demo CSVs; never committed
    └── render.yaml              # Render Blueprint: API plus Postgres

## Local development

Run the API:

    cd backend
    Copy-Item .env.example .env
    # Replace JWT_SECRET in .env with a random value of at least 32 characters.
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000

Run the frontend in a second terminal:

    cd frontend
    Copy-Item .env.example .env.local
    npm ci
    npm run dev

For the full model-training workflow, including how to run hospital clients, see the deployment guide.
