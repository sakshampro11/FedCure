# FedCure - Privacy-Preserving Federated Learning for Heart Disease Prediction

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

| Layer       | Technology                                    |
|-------------|-----------------------------------------------|
| Backend     | Python, FastAPI, SQLAlchemy, PyTorch           |
| Frontend    | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| FL Client   | Python, PyTorch, Docker                        |
| Database    | SQLite                                         |
| Privacy     | Differential Privacy (Gaussian Noise, epsilon) |
| Aggregation | Federated Averaging (FedAvg)                   |

---

## Project Structure

```
fedCure/
├── main.py                  # FastAPI backend server
├── ml_model.py              # HeartDiseaseModel (13->128->64->32->1)
├── models.py                # SQLAlchemy database models
├── federated.py             # FedAvg aggregation logic
├── training.py              # Training utilities
├── requirements.txt         # Python dependencies
├── Dockerfile               # Backend Docker image
├── docker-compose.yml       # Full-stack orchestration
├── railway.json             # Railway backend deployment
├── vercel.json              # Vercel frontend deployment
├── .env.example             # Environment variables template
│
├── client/                  # FL Hospital Client
│   ├── Dockerfile
│   ├── fedcure_client.py    # Local training + DP noise + weight submission
│   └── requirements.txt
│
├── data/                    # Dataset & preprocessing scripts
│   ├── prepare_dataset.py   # Download + clean UCI Heart Disease data
│   ├── train_baseline.py    # Centralized baseline model training
│   ├── split_for_hospitals.py # Split data for 4 simulated hospitals
│   ├── heart_disease_clean.csv
│   ├── hospital_1.csv ... hospital_4.csv
│   └── baseline_accuracy.txt
│
├── models/                  # Saved model weights
│   └── baseline_model.pt
│
└── frontend/                # Next.js Dashboard
    ├── src/app/
    │   ├── page.tsx         # Landing page
    │   ├── login/page.tsx   # Hospital login
    │   ├── register/page.tsx # Hospital registration
    │   └── dashboard/page.tsx # Main dashboard
    └── src/lib/api.ts       # API client
```

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional, for containerized setup)

### 1. Clone & Setup Backend

```bash
git clone https://github.com/sakshampro11/FedCure.git
cd FedCure

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
pip install scikit-learn       # For data prep scripts
```

### 2. Prepare Dataset

```bash
python data/prepare_dataset.py       # Download & clean UCI Heart Disease data
python data/train_baseline.py        # Train centralized baseline (comparison)
python data/split_for_hospitals.py   # Split data for 4 simulated hospitals
```

### 3. Start Backend Server

```bash
uvicorn main:app --reload
# Server runs at http://localhost:8000
```

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard runs at http://localhost:3000
```

### 5. Register Hospitals & Run FL Clients

```bash
# Register 4 hospitals via the web UI or API:
curl -X POST http://localhost:8000/api/hospitals/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Hospital Alpha","location":"New York","admin_email":"admin@alpha.med"}'

# Note the API key from the response, then run FL clients:
set API_KEY=<api-key-from-registration>
set HOSPITAL_ID=1
set SERVER_URL=http://localhost:8000
python client/fedcure_client.py
```

---

## Docker Compose (Full Demo)

Run the entire stack with a single command:

```bash
# 1. Copy and fill in environment variables
cp .env.example .env
# Edit .env with your hospital API keys

# 2. Start everything
docker-compose up --build

# This starts:
#   - Backend server    (port 8000)
#   - Frontend dashboard (port 3000)
#   - 4 FL hospital clients (auto-train)
```

---

## Environment Variables

| Variable             | Default                   | Description                              |
|----------------------|---------------------------|------------------------------------------|
| `DATABASE_URL`       | `sqlite:///./fedcure.db`  | Database connection string               |
| `JWT_SECRET`         | (required in production)  | Secret key for JWT tokens                |
| `ALLOWED_ORIGINS`    | `http://localhost:3000`   | CORS allowed origins                     |
| `NEXT_PUBLIC_API_URL`| `http://localhost:8000`   | Backend URL for frontend API calls       |
| `HOSPITAL_X_API_KEY` | (from registration)       | API keys for FL client authentication    |
| `SERVER_URL`         | `http://localhost:8000`   | Backend URL for FL clients               |
| `HOSPITAL_ID`        | (required)                | Unique hospital identifier               |
| `NUM_ROUNDS`         | `5`                       | Number of FL training rounds             |
| `EPOCHS_PER_ROUND`   | `3`                       | Local training epochs per round          |

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

1. **Initialization**: Server creates a global HeartDiseaseModel
2. **Download**: Each hospital downloads the current global model
3. **Local Training**: Hospitals train on their private data (3-5 epochs)
4. **Differential Privacy**: Gaussian noise (sigma=0.01) is added to trained weights
5. **Upload**: Hospitals submit noisy weight gradients to the server
6. **Aggregation**: When 4 hospitals submit, FedAvg averages the weights
7. **Update**: New global model is saved; dashboard updates in real-time
8. **Repeat**: Process continues for 5-10 rounds until convergence

---

## Deployment

### Backend (Railway)
- Push to GitHub and connect to [Railway](https://railway.app)
- Railway will auto-detect `railway.json` and build from `Dockerfile`
- Set environment variables in Railway dashboard

### Frontend (Vercel)
- Connect repo to [Vercel](https://vercel.com)
- Vercel will auto-detect `vercel.json`
- Set `NEXT_PUBLIC_API_URL` to your Railway backend URL

---

## License

MIT License - Built for HackBVP Hackathon
