# FedCure — Privacy-Preserving Federated Learning for Heart Disease Prediction

FedCure enables multiple hospitals to collaboratively train a heart disease prediction model **without sharing patient data**. Using Federated Learning with Differential Privacy, each hospital trains locally and only shares encrypted model weight gradients with the central aggregator.

---

## Architecture

```
+-------------------+     +-------------------+     +-------------------+
|   Hospital 1      |     |   Hospital 2      |     |   Hospital 3      |
|   (FL Client)     |     |   (FL Client)     |     |   (FL Client)     |
|                   |     |                   |     |                   |
|  Local Patient    |     |  Local Patient    |     |  Local Patient    |
|  Data (Private)   |     |  Data (Private)   |     |  Data (Private)   |
+--------+----------+     +--------+----------+     +--------+----------+
         |                         |                         |
         |    Weight Gradients     |   Weight Gradients      |
         |    (+ DP Noise)         |   (+ DP Noise)          |
         v                         v                         v
+------------------------------------------------------------------------+
|                     FedCure Central Server                              |
|                     (FastAPI + FedAvg Aggregator)                       |
|                                                                        |
|   [Global Model]  <--  FedAvg Aggregation  <--  Noisy Weight Updates   |
|   [SQLite DB]          (Weighted Average)                              |
|   [REST API]                                                           |
+-----------------------------------+------------------------------------+
                                    |
                                    | HTTPS API
                                    v
                        +-----------+-----------+
                        |   FedCure Dashboard   |
                        |   (Next.js Frontend)  |
                        |                       |
                        |  - Training Metrics   |
                        |  - Accuracy Charts    |
                        |  - Inference Tool     |
                        |  - Node Setup Guide   |
                        +-----------------------+
```

---

## Tech Stack

| Layer       | Technology                                      |
|-------------|--------------------------------------------------|
| Backend     | Python, FastAPI, SQLAlchemy, PyTorch             |
| Frontend    | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui  |
| FL Client   | Python, PyTorch, Docker                          |
| Database    | SQLite                                           |
| Privacy     | Differential Privacy (Gaussian Noise, epsilon)   |
| Aggregation | Federated Averaging (FedAvg)                     |

---

## Project Structure

```
FedCure/
│
├── server/                      # FastAPI Backend
│   ├── Dockerfile               # Backend Docker image
│   ├── main.py                  # FastAPI app, routes, and FL round logic
│   ├── db_models.py             # SQLAlchemy database models
│   ├── federated.py             # FedAvg aggregation logic
│   └── nn_model.py              # HeartDiseaseModel (13→128→64→32→1)
│
├── client/                      # FL Hospital Client
│   ├── Dockerfile               # Client Docker image (distributed to hospitals)
│   ├── fedcure_client.py        # Local training + DP noise + weight submission
│   └── requirements.txt
│
├── frontend/                    # Next.js Dashboard
│   ├── src/app/
│   │   ├── page.tsx             # Landing page
│   │   ├── login/page.tsx       # Hospital login
│   │   ├── register/page.tsx    # Hospital registration
│   │   └── dashboard/page.tsx   # Main FL training dashboard
│   └── src/lib/api.ts           # API client
│
├── data/                        # Hospital training data (git-ignored CSVs)
│   ├── hospital_1.csv
│   ├── hospital_2.csv
│   ├── hospital_3.csv
│   └── hospital_4.csv
│
├── temp_scripts/                # One-time setup scripts (not part of live system)
│   ├── README.md
│   └── prepare_dataset.py       # Cleans raw Kaggle CSV and splits into hospital CSVs
│
├── models/                      # Saved global model weights (git-ignored)
│
├── requirements.txt             # Root Python dependencies (for server)
├── docker-compose.yml           # Full-stack orchestration
├── railway.json                 # Railway backend deployment config
├── vercel.json                  # Vercel frontend deployment config
├── .env.example                 # Environment variables template
└── .gitignore
```

> **Note:** `data/*.csv`, `models/`, `*.pt`, and `.env` are all git-ignored. Patient data never leaves the hospital machines.

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for running FL clients as containers)

### 1. Clone & Setup

```bash
git clone https://github.com/sakshampro11/FedCure.git
cd FedCure

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings (see Environment Variables section below)
```

### 3. (First-time only) Prepare Hospital Datasets

If you're setting up fresh, you need to generate the 4 hospital CSV files from the raw Kaggle dataset.

```bash
# Download the dataset from Kaggle:
# https://www.kaggle.com/datasets/sid321axn/heart-statlog-cleveland-hungary-final
# Place the CSV somewhere accessible, then run:

python temp_scripts/prepare_dataset.py <path-to-raw-kaggle-csv>
# Outputs: data/hospital_1.csv through data/hospital_4.csv
```

> The `temp_scripts/` folder can be deleted after this step — it's only needed for initial setup.

### 4. Start the Backend Server

Run from the **project root** (not from inside `server/`):

```bash
uvicorn server.main:app --reload
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard runs at http://localhost:3000
```

### 6. Register Hospitals

Register hospitals via the web UI at `http://localhost:3000/register`, or via the API:

```bash
curl -X POST http://localhost:8000/api/hospitals/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Hospital Alpha","location":"New York","admin_email":"admin@alpha.med"}'
# Save the returned api_key — you'll need it to run the FL client
```

### 7. Run the FL Client (Docker)

Build the client image once from the `client/` directory:

```bash
cd client
docker build -t fedcure-client .
```

Then run it for each hospital (substitute your actual `API_KEY` and `HOSPITAL_ID`):

```bash
# From the directory containing the hospital's CSV file:
docker run --rm `
  -e SERVER_URL="http://host.docker.internal:8000" `
  -e API_KEY="<your-hospital-api-key>" `
  -e HOSPITAL_ID=1 `
  -e NUM_ROUNDS=5 `
  -e EPOCHS_PER_ROUND=3 `
  -v "${PWD}/hospital_1.csv:/data/hospital.csv" `
  fedcure-client
```

> **Important:** Use `host.docker.internal` (not `localhost`) to reach the server from inside Docker on Windows/macOS.

---

## Docker Compose (Full Demo)

Run the entire stack with a single command:

```bash
# 1. Copy and configure environment variables
cp .env.example .env
# Edit .env with your hospital API keys (register hospitals first via the UI)

# 2. Build and start everything
docker-compose up --build

# This starts:
#   - Backend server     (port 8000)
#   - Frontend dashboard (port 3000)
#   - 4 FL hospital clients (auto-train)
```

---

## Environment Variables

### Server (`.env` in project root)

| Variable             | Default                    | Description                              |
|----------------------|----------------------------|------------------------------------------|
| `DATABASE_URL`       | `sqlite:///./fedcure.db`   | Database connection string               |
| `JWT_SECRET`         | (required in production)   | Secret key for JWT tokens                |
| `ALLOWED_ORIGINS`    | `http://localhost:3000`    | CORS allowed origins (comma-separated)   |

### Frontend (`frontend/.env.local`)

| Variable               | Default                   | Description                         |
|------------------------|---------------------------|-------------------------------------|
| `NEXT_PUBLIC_API_URL`  | `http://localhost:8000`   | Backend URL for frontend API calls  |

### FL Client (environment variables passed to Docker)

| Variable             | Default                    | Description                              |
|----------------------|----------------------------|------------------------------------------|
| `SERVER_URL`         | `http://localhost:8000`    | Backend URL for FL clients               |
| `API_KEY`            | (required)                 | Hospital API key (from registration)     |
| `HOSPITAL_ID`        | (required)                 | Unique hospital identifier               |
| `DATA_PATH`          | `/data/hospital.csv`       | Path to hospital CSV inside container    |
| `NUM_ROUNDS`         | `5`                        | Number of FL training rounds             |
| `EPOCHS_PER_ROUND`   | `3`                        | Local training epochs per round          |

---

## API Endpoints

| Method | Endpoint                        | Description                         |
|--------|---------------------------------|-------------------------------------|
| GET    | `/api/health`                   | Health check                        |
| POST   | `/api/hospitals/register`       | Register a new hospital             |
| POST   | `/api/hospitals/login`          | Login with API key                  |
| POST   | `/api/training/submit-weights`  | Submit local model weights          |
| GET    | `/api/training/status`          | Get current training status         |
| GET    | `/api/training/global-model`    | Download global model weights       |
| GET    | `/api/dashboard/metrics`        | Get all training round metrics      |
| POST   | `/api/inference/predict`        | Predict heart disease risk          |

---

## How Federated Learning Works in FedCure

1. **Initialization**: Server creates a global `HeartDiseaseModel`
2. **Download**: Each hospital downloads the current global model weights
3. **Local Training**: Hospital trains on its private data for 3–5 epochs
4. **Differential Privacy**: Gaussian noise (`sigma=0.01`) is added to trained weights
5. **Upload**: Hospital submits noisy weight gradients to the server
6. **Aggregation**: Once all participating hospitals have submitted, FedAvg averages the weights
7. **Update**: New global model is saved; dashboard updates in real-time
8. **Repeat**: Process continues for the configured number of rounds until convergence

> The server tracks **unique hospitals** per round — re-submissions from the same hospital in the same round are deduplicated, ensuring fair aggregation.

---

## Deployment

### Backend (Railway)
- Push to GitHub and connect to [Railway](https://railway.app)
- Railway auto-detects `railway.json` and builds from `server/Dockerfile`
- The start command is `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
- Set environment variables (`DATABASE_URL`, `JWT_SECRET`, `ALLOWED_ORIGINS`) in the Railway dashboard

### Frontend (Vercel)
- Connect repo to [Vercel](https://vercel.com)
- Vercel auto-detects `vercel.json`
- Set `NEXT_PUBLIC_API_URL` to your Railway backend URL in Vercel's environment settings

---

## Recent Changes

| Change | Description |
|--------|-------------|
| **Server modularised into `server/`** | `main.py`, `db_models.py`, `federated.py`, `nn_model.py` and `Dockerfile` are now under `server/`. Run the backend with `uvicorn server.main:app --reload` from the project root. |
| **Dependency-free `.env` loader** | Both `server/main.py` and `client/fedcure_client.py` load `.env` files without requiring `python-dotenv`, using a built-in parser. |
| **DP noise bug fix** | Fixed a `TypeError: iteration over a 0-d tensor` in the Differential Privacy noise function in `client/fedcure_client.py`. |
| **Hospital deduplication fix** | Fixed a bug where multiple weight submissions from the same hospital in the same round were counted as separate participants, inflating the hospital count on the dashboard. |
| **Baseline accuracy removed** | The centralized baseline accuracy metric has been fully removed — from `server/db_models.py`, `server/main.py`, and the frontend dashboard (`frontend/src/app/dashboard/page.tsx`). FedCure now purely tracks federated model accuracy. |
| **Legacy scripts cleaned up** | Old scripts (`train_baseline.py`, `split_for_hospitals.py`, `eval_models.py`, `simulate_training.py`, `diagnose_model.py`, etc.) have been removed. The only setup script remaining is `temp_scripts/prepare_dataset.py`. |

---

## License

MIT License — Built for HackBVP 7.0 Hackathon
