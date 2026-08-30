Privacy-Preserving Federated Learning Framework for Collaborative Healthcare Analysis: A Case Study on Heart Disease Prediction

**MINI PROJECT SYNOPSIS**

BACHELOR OF TECHNOLOGY  
*in*  
COMPUTER SCIENCE & ENGINEERING  
*by*

| PRATHAM CHHABRA Enrollment No.: 00511502723 | SAKSHAM BUDHIRAJA Enrollment No.: 01411502723 | RIYA RAJ Enrollment No.: 05511502723 |
| :---: | :---: | :---: |

*Guided by*  
Mr. Mohit Tiwari  
Assistant Professor

DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING  
BHARATI VIDYAPEETH'S COLLEGE OF ENGINEERING  
(AFFILIATED TO GURU GOBIND SINGH INDRAPRASTHA UNIVERSITY, DELHI)  
DELHI-110063  
SEPTEMBER 2026

## **Introduction**

Healthcare is undergoing a major transformation with the adoption of artificial intelligence (AI) and machine learning (ML). Predictive models built on medical data have the potential to revolutionize disease diagnosis, prognosis, and treatment planning. For example, ML models can predict the likelihood of cardiovascular conditions, detect anomalies in radiological images, or recommend drug dosages personalized to patients.

However, healthcare data is not only highly sensitive but also distributed across multiple institutions such as hospitals, laboratories, and research centers. The strict privacy regulations under HIPAA and GDPR prohibit the sharing of raw patient data between organizations. Consequently, data remains siloed within institutions, limiting the diversity and generalizability of predictive models. A model trained on data from one hospital may fail to perform well on another due to differences in demographics, medical practices, or recording standards.

Traditional centralized ML methods require aggregating all patient data in a single repository. While this approach maximizes data availability, it is highly impractical in healthcare because of legal restrictions, security risks, and the cost of transferring large-scale sensitive datasets. These limitations create a pressing need for **privacy-preserving collaborative learning frameworks** that allow institutions to build robust models without violating data privacy.

**Federated Learning (FL)** has emerged as a promising solution to this challenge. FL enables multiple institutions to collaboratively train a model without sharing raw data. Instead, each institution trains the model locally, and only the model updates (weights or gradients) are sent to a central server for aggregation. This approach reduces the privacy risks associated with data centralization. However, FL alone does not guarantee security. Studies have shown that adversaries can reconstruct sensitive information or perform inference attacks using gradients exchanged during FL.

To address this vulnerability, **privacy-preserving techniques** must be layered on top of FL. **Differential Privacy (DP)** provides a mathematical guarantee by adding noise to updates, making it difficult to trace back individual contributions. In this project, Gaussian noise is injected directly into model weight gradients before submission to the central server, providing a practical, implementable layer of privacy protection.

In this project, we have designed and implemented **FedCure** — a fully functional, end-to-end privacy-preserving federated learning platform for healthcare applications. Heart disease prediction using a combined multi-source dataset serves as a case study, while the framework itself is designed to be extensible to a wide range of healthcare scenarios.

## **Problem Statement**

This project designs and evaluates a privacy-preserving federated learning framework for healthcare applications, using heart disease prediction as a case study. The framework enables multiple hospitals to collaboratively train machine learning models without centralizing sensitive patient data, thereby addressing challenges posed by regulations such as HIPAA and GDPR. To strengthen privacy, the system integrates **Differential Privacy (DP)** through Gaussian noise injection into weight gradients, ensuring secure model updates while minimizing the risk of data leakage. The performance of the proposed framework is compared with a centralized baseline in terms of predictive accuracy, privacy guarantees, and system scalability.

## **Literature Review**

### **A. Centralized ML in Healthcare**

* **Advantages**: Traditional approaches like those in Kermany **et al.** and Rajkomar **et al.** enable highly accurate predictions by pooling data.

* **Limitations**: These methods are impractical in multi-institutional settings due to privacy regulations and inherent data silos.

* **Takeaway**: While effective, centralized systems cannot scale across institutions without violating patient privacy.

### **B. Federated Learning (FL) in Healthcare**

* McMahan **et al.** introduced FL to preserve data locality during collaborative model training.

* Sheller **et al.** applied FL to brain tumor segmentation successfully, demonstrating parity with centralized models while enhancing privacy.

* **Advantages**: FL allows multi-institutional collaboration without data sharing.

* **Limitations**: FL performance can suffer from non-IID data distributions, communication inefficiencies, and model convergence issues.

### **C. Early Privacy Enhancements: DP & HE**

* **Differential Privacy (DP)** pioneered by Dwork, further integrated into deep learning by Abadi **et al**.

  * **Advantage**: Protects individual contributions within updates.

  * **Limitation**: Introduces a privacy-utility trade-off - stronger privacy often reduces model accuracy.

* **Homomorphic Encryption (HE)**, as proposed by Gentry, enables encrypted aggregation.

  * **Advantage**: Enables secure model update aggregation without decryption.

  * **Limitation**: Computational overhead can be prohibitive for large-scale models.

### **D. Recent Advances (2023-2025)**

1. **Haj Fares & Emam Saad (2024)** - "DPResNet for Medical Imaging"  
    - Introduces a modified ResNet model using DP and secure aggregation for BloodMNIST dataset.  
    - **Advantages**: Achieves accuracy nearly equal to non-private models.  
    - **Limitation**: Requires careful tuning of the noise to balance privacy and performance.  
    [arXiv](https://arxiv.org/abs/2412.00687)

2. **Ahmed et al. (2024)** - *Adaptive DP-FL for COVID-19 X-Ray Classification*  
    - Proposes an adaptive DP mechanism that adjusts noise based on data sensitivity.  
    - **Advantages**: Improves prediction accuracy (+1%) and reduces communication rounds.  
    - **Limitation**: Minor reduction (~3%) in accuracy due to noise, illustrating the privacy-accuracy trade-off.  
    [Frontiers](https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2024.1409314/full)

3. **Singh et al. (2025)** - *Hierarchical FL with DP & Secure MPC*  
    - Introduces hierarchical federated architecture with DP and MPC to strengthen privacy and efficiency.  
    - **Advantages**: Offers resilient and scalable privacy-preserving model training.  
    - **Limitation**: Increased complexity in system design and implementation.  
    [MDPI](https://www.mdpi.com/1999-5903/17/8/345)

4. **Xie et al. (2025)** - *Adaptive DP with Dual-Layer Protection*  
    - Proposes adaptive noise budgets and dual-layer DP in medical FL.  
    - **Advantages**: Strong resistance to membership inference attacks and high model accuracy (92.5%).  
    - **Limitation**: The framework's theoretical complexity may impede practical deployment.  
    [Journal of Knowledge](https://jklst.org/index.php/home/article/view/280)

### **E. Comparative Summary**

| Study | Strategy | Dataset/Application | Privacy Strength | Accuracy | Limitations |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Haj Fares & Emam Saad (2024) | DP + Secure Aggregation | BloodMNIST Medical Imaging | Medium | Near baseline | Fine-tuning required |
| Ahmed et al. (2024) | Adaptive DP-FL | COVID-19 X-Ray | High | -3% base; +1% improved | Complexity of adaptation |
| Singh et al. (2025) | FL + DP + Secure MPC | Healthcare (General) | High | Comparable | Architectural complexity |
| Xie et al. (2025) | Dual-Layer Adaptive DP | Medical Data Collaboration | Very High | 92.5% | Theoretical complexity |

### **F. Relevance to This Project**

These works highlight the evolving landscape of FL in healthcare: from early DP implementations to advanced hierarchical and adaptive privacy techniques. FedCure directly addresses this space by implementing a practical, deployable FL system with weight-level Gaussian noise DP. Unlike purely theoretical frameworks, FedCure provides a complete full-stack solution — including a REST API central server, containerized hospital clients, and a real-time web dashboard — demonstrating that privacy-preserving FL is viable even in resource-constrained hackathon settings.

## **Objectives**

The project's primary objectives are as follows:

1. **Centralized Baseline:** Build and evaluate a centralized ML model for heart disease prediction to serve as a benchmark.

2. **Federated Learning Framework:** Develop a custom federated learning system simulating collaboration among 4 hospitals using Federated Averaging (FedAvg).

3. **Differential Privacy Integration:** Incorporate Gaussian noise injection at the weight level to defend against inference attacks, with configurable noise scale (sigma).

4. **End-to-End System Implementation:** Build and deploy a complete platform including:
   - A **FastAPI** REST server as the central aggregation coordinator
   - A **PyTorch**-based neural network (11->32->16->1) for binary heart disease classification
   - A **Dockerized FL client** for hospital-side local training and weight submission
   - A **Next.js 14** web dashboard for real-time training monitoring and clinical inference

5. **Comparative Analysis:** Evaluate the federated model against a centralized baseline in terms of accuracy, precision, recall, F1-score, and AUC, quantifying the privacy-utility trade-off.

6. **Clinical Inference Tool:** Provide a multi-step patient assessment form on the dashboard that uses the live global model to predict heart disease risk, returning a probability score and risk classification (Low / Moderate / High).

7. **Generalizability:** Ensure the framework remains extensible to other healthcare prediction tasks beyond heart disease.

## **Methodology**

FedCure was implemented as a complete end-to-end system across four phases.

### **1. Dataset & Preprocessing**

**Dataset:** Combined Heart Disease Dataset (~1190 samples) — a multi-source aggregation of the Cleveland, Hungarian, Switzerland, Long Beach VA, and Statlog datasets (sourced from Kaggle: `heart-statlog-cleveland-hungary-final`).

**Features (11 input + 1 target):**

| # | Feature | Code Name | Type | Description |
|---|---------|-----------|------|-------------|
| 1 | Age | `age` | int | Patient age in years (28-77) |
| 2 | Sex | `sex` | binary | 0 = Female, 1 = Male |
| 3 | Chest Pain Type | `cp` | categorical | 1-4 (Typical, Atypical, Non-anginal, Asymptomatic) |
| 4 | Resting Blood Pressure | `trestbps` | int | mm Hg on admission (80-220) |
| 5 | Cholesterol | `chol` | int | Serum cholesterol mg/dl (100-600) |
| 6 | Fasting Blood Sugar | `fbs` | binary | 1 if > 120 mg/dl, else 0 |
| 7 | Resting ECG | `restecg` | categorical | 0 = Normal, 1 = ST-T abnormality, 2 = LV Hypertrophy |
| 8 | Max Heart Rate | `thalach` | int | Maximum heart rate achieved (50-220) |
| 9 | Exercise Induced Angina | `exang` | binary | 1 = Yes, 0 = No |
| 10 | ST Depression | `oldpeak` | float | ST depression induced by exercise (0.0-6.2) |
| 11 | ST Slope | `slope` | categorical | 0 = Upsloping, 1 = Flat, 2 = Downsloping |
| **Target** | Heart Disease | `target` | binary | 0 = No disease, 1 = Disease present |

**Preprocessing Pipeline:** Raw column names renamed for code compatibility; zero-valued cholesterol and resting BP (placeholder values in Hungarian/Swiss data) replaced with column medians; extreme values clipped to physiological ranges; binary target validated. **Feature Scaling:** StandardScaler (Z-score normalization) is applied uniformly across all training scripts and the inference endpoint, using hardcoded per-feature means and standard deviations computed from the full dataset.

**Hospital Partitioning:** The dataset is divided into **4 equal, non-overlapping subsets** (~298 samples each) representing 4 collaborating hospitals. During simulation, each hospital uses a random 25% subset per round to model realistic participation.

### **2. Machine Learning Model**

A compact **PyTorch** neural network was designed for binary classification:

```
Input (11 features)
    ? Linear(11 ? 32) ? BatchNorm1d(32) ? ReLU ? Dropout(0.3)
    ? Linear(32 ? 16) ? BatchNorm1d(16) ? ReLU ? Dropout(0.3)
    ? Linear(16 ? 1)  ? Sigmoid
Output: Risk score in [0, 1]
```

| Design Choice | Rationale |
|---------------|-----------|
| Compact architecture (11?32?16?1) | With ~298 samples per hospital, a larger model would overfit severely |
| BatchNorm1d | Stabilizes training when data distributions vary across hospitals |
| Dropout(0.3) | Regularization to prevent overfitting on small local subsets |
| Sigmoid output | Produces an interpretable probability score (heart disease risk) |
| BCELoss + Adam optimizer | Standard binary classification setup; Adam handles noisy gradients well |

**Training hyperparameters:** Learning rate = 0.001, Weight decay = 0.001, Batch size = 32, Gradient clipping (max_norm = 1.0), Local epochs per FL round = 5.

### **3. Federated Learning Protocol**

The FL system implements the standard **FedAvg (Federated Averaging)** algorithm from scratch in Python:

```
Server maintains global model v{N}
¦
+-- 4 hospital clients download global model
¦   +-- Each trains locally for 5 epochs on private data
¦   +-- Adds Gaussian DP noise (sigma = 0.005) to all weight tensors
¦   +-- Submits noisy weight gradients via HTTP POST
¦
+-- Server: once 4 unique hospitals have submitted:
    +-- FedAvg: element-wise mean of all 4 weight tensors
    +-- Saves new global model v{N+1}
    +-- Records round accuracy and epsilon in SQLite database
    +-- New model available for next round
```

**10 federated rounds** have been completed, producing model versions v0 through v10.

**Differential Privacy:** Gaussian noise with sigma = 0.005 is added to each parameter tensor after local training:

```
noisy_weight = weight + Gaussian(0, sigma^2)
```

This provides a practical privacy shield against gradient inversion attacks while maintaining model utility. Empirical testing showed that sigma >= 0.01 caused prediction saturation (all outputs converging to 1.0), making sigma = 0.005 the practical sweet spot for this dataset size.

### **4. Full-Stack System Architecture**

FedCure is a fully deployed, production-ready platform consisting of four integrated components:

#### **A. Backend Server (FastAPI)**

A **FastAPI** REST API serves as the central FL coordinator:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check (Docker/Railway monitoring) |
| `/api/hospitals/register` | POST | Register a new hospital, returns UUID API key |
| `/api/hospitals/login` | POST | Authenticate via API key, returns access token |
| `/api/training/global-model` | GET | Download current global model weights as JSON |
| `/api/training/submit-weights` | POST | Accept local model weights from a hospital |
| `/api/training/status` | GET | Current round, accuracy, pending submissions count |
| `/api/dashboard/metrics` | GET | All training rounds for chart visualization |
| `/api/inference/predict` | POST | Patient vitals ? risk score + risk classification |

**Database (SQLite via SQLAlchemy):** Three tables — `hospitals` (name, location, email, UUID API key), `training_rounds` (round number, federated accuracy, privacy epsilon, hospital count), and `model_versions` (version tag, file path, accuracy).

The server tracks **unique hospital submissions** per round using an in-memory set, ensuring each hospital contributes exactly once per aggregation. FedAvg triggers automatically when all 4 required hospitals have submitted.

#### **B. FL Hospital Client (Python + Docker)**

A standalone Python script (`client/fedcure_client.py`) runs inside a **Docker container** at each participating hospital. Configuration is fully environment-variable-driven (`SERVER_URL`, `API_KEY`, `HOSPITAL_ID`, `NUM_ROUNDS`, `EPOCHS_PER_ROUND`). The client:

1. Downloads the current global model via `GET /api/training/global-model`
2. Reconstructs the PyTorch model from JSON weights
3. Trains locally on the hospital's private CSV data (StandardScaler applied)
4. Injects Gaussian DP noise (sigma = 0.01 in deployed client) into all weight tensors
5. Submits noisy weights via `POST /api/training/submit-weights`
6. Sleeps 10 seconds and repeats for the configured number of rounds

The client contains its own copy of the `HeartDiseaseModel` class (identical to the server's `nn_model.py`) to operate fully independently without server-side imports.

#### **C. Frontend Dashboard (Next.js 14)**

A modern web application provides real-time visibility into the FL system and a clinical prediction tool:

| Page | Purpose |
|------|---------|
| `/` | Landing page — hero section with infinite-scroll medical image carousel, features bento grid, 4-step "How It Works" explainer, CTA footer |
| `/register` | Hospital onboarding — collects name, location, email; displays generated API key and hospital ID on success |
| `/login` | Hospital authentication — API key login, stores JWT in localStorage |
| `/dashboard` | Main control panel — 4 live metric cards (round number, hospitals, privacy epsilon, federated accuracy), accuracy timeline chart comparing federated vs. baseline, privacy mechanism explanation card, 3-step clinical inference wizard |

The dashboard **auto-refreshes metrics every 10 seconds** via polling. The clinical inference wizard collects patient vitals across 3 steps (Patient Info ? Vital Signs ? Cardiac Stress) and displays results in an animated **RiskGauge** circular SVG component with color-coded risk levels (green/yellow/red).

**Technology stack:** Next.js 14 (App Router), TypeScript, TailwindCSS 3.4, shadcn/ui component library, Recharts (line charts), Axios (API client with JWT interceptor), Lucide React (icons), Geist font.

#### **D. Deployment (Cloud-Ready)**

| Platform | Component | Configuration |
|----------|-----------|---------------|
| **Railway** | Backend FastAPI server | `railway.json` — Dockerfile-based, health check at `/api/health`, dynamic `$PORT` binding |
| **Vercel** | Frontend Next.js dashboard | `vercel.json` — builds from `frontend/`, injects `NEXT_PUBLIC_API_URL` |
| **Docker Compose** | Full local stack | Orchestrates backend + 4 hospital clients + frontend with volume-mounted CSVs |

### **5. Evaluation & Results**

**Federated vs. Centralized Comparison (after 10 FL rounds):**

| Metric | Federated Model | Centralized Baseline |
|--------|----------------|----------------------|
| Test Accuracy | ~82% | ~85% |
| Raw Data Sharing | Zero — weights only | Full dataset centralized |
| Privacy Guarantee | Gaussian DP noise (sigma = 0.005) | None |
| Multi-Hospital Support | Native (4 hospitals) | Not applicable |

**Privacy-Utility Trade-off:** Lower DP noise (sigma = 0.005) preserves model utility while providing meaningful protection against gradient inversion attacks. This represents a ~3% accuracy cost versus centralized training — consistent with findings in the literature.

**Inference Risk Thresholds:**
- **Low Risk**: risk score < 0.30
- **Moderate Risk**: 0.30 <= risk score <= 0.70
- **High Risk**: risk score > 0.70

## **Technology Stack Summary**

| Layer | Technology |
|-------|-----------|
| ML Framework | PyTorch (neural network, FedAvg, DP noise injection) |
| Backend API | FastAPI + Uvicorn (Python 3.10+) |
| Database | SQLite via SQLAlchemy ORM |
| Data Processing | Pandas, NumPy, scikit-learn (StandardScaler) |
| FL Client | Python + Docker (containerized per hospital) |
| Frontend | Next.js 14, TypeScript, TailwindCSS 3.4, shadcn/ui, Recharts |
| Orchestration | Docker Compose (full-stack local demo) |
| Cloud Deployment | Railway (backend), Vercel (frontend) |

## **Future Scope**

This project delivers a working, deployed privacy-preserving federated learning platform. The following directions extend its impact:

1. **Formal DP Guarantees:** The current Gaussian noise mechanism provides practical protection but is not formally bounded by an epsilon-delta privacy budget. Future work can replace it with **DP-SGD** (Abadi et al.) or the **Renyi Differential Privacy** framework, enabling provable (epsilon, delta)-DP guarantees with tight epsilon accounting across rounds.

2. **Homomorphic Encryption (HE):** Encrypting model weight updates before transmission to the server (e.g., using Microsoft SEAL or TenSEAL) would ensure the central aggregator cannot inspect individual hospital contributions, eliminating the trusted-server assumption.

3. **Secure Multi-Party Computation (SMPC):** Replacing simple FedAvg with a cryptographic secure aggregation protocol would eliminate the need to trust the central server entirely.

4. **Non-IID Data Handling:** The current system uses IID partitioning (equal random splits). Real hospital data is highly heterogeneous. Future work can explore FedProx, SCAFFOLD, or personalized federated learning strategies to handle non-IID distributions.

5. **Explainability in Federated Models:** Integrating **SHAP or LIME** into the inference pipeline would allow clinicians to understand which features drove a particular risk prediction, building clinical trust and ensuring regulatory compliance.

6. **Real-World Deployment:** Moving from simulated hospital clients to actual hospital systems (e.g., integrating with MIMIC-III EHRs or real hospital information systems) and stress-testing at scale on cloud infrastructure would validate production readiness.

7. **Multi-Modal Healthcare Data:** Extending the framework to handle medical imaging (X-rays, MRI scans) alongside structured EHR data, or genomic data from wearable devices, would create a holistic privacy-preserving healthcare analytics ecosystem.

8. **Policy & Regulatory Alignment:** Adding compliance monitoring for **HIPAA, GDPR, and India's Digital Personal Data Protection Act 2023** would make the system directly deployable in regulated healthcare environments.

## **References**

\[1\] D. Kermany *et al.*, "Identifying medical diagnoses and treatable diseases by image-based deep learning," *PubMed/ScienceDirect*, 2018.

\[2\] A. Rajkomar *et al.*, "Scalable and accurate deep learning with electronic health records," *npj Digital Medicine*, 2018.

\[3\] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. Arcas, "Communication-efficient learning of deep networks from decentralized data," in *Proc. AISTATS*, 2017. https://arxiv.org/abs/1602.05629

\[4\] L. E. Sheller *et al.*, "Federated learning in medicine: Facilitating multi-institutional collaborations without sharing patient data," *Scientific Reports*, 2020. Available: https://digitalcommons.wustl.edu

\[5\] M. Abadi *et al.*, "Deep learning with differential privacy," in *Proc. CCS*, 2016. https://arxiv.org/abs/1607.00133

\[6\] C. Dwork, "Differential privacy," in *Proc. ICALP*, 2006. Available: https://dwork.seas.harvard.edu

\[7\] C. Gentry, "A fully homomorphic encryption scheme," Stanford University, Thesis, 2009. https://crypto.stanford.edu

\[8\] S. Madathil, "Revolutionizing healthcare data analytics with federated learning," 2025.

\[9\] P. Koutsoubis, "Privacy-preserving federated learning and uncertainty quantification," 2025.

\[10\] R. Haripriya, "Privacy-preserving federated learning for collaborative medical data mining," 2025.

\[11\] Sid321axn, "Heart Statlog Cleveland Hungary Final," *Kaggle Dataset*, 2022. Available: https://www.kaggle.com/datasets/sid321axn/heart-statlog-cleveland-hungary-final

\[12\] A. Paszke *et al.*, "PyTorch: An imperative style, high-performance deep learning library," in *Proc. NeurIPS*, 2019. https://arxiv.org/abs/1912.01703

\[13\] S. Ramon and T. Duan, "FastAPI: Modern, fast (high-performance) web framework for building APIs with Python 3.6+," 2018. Available: https://fastapi.tiangolo.com
