import axios from "axios";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("fedcure_jwt");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export interface HospitalRegistration {
  hospital_id: number;
  api_key: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
}

export interface TrainingRound {
  round_number: number;
  accuracy_federated: number;
  epsilon: number;
  num_hospitals: number;
  created_at: string;
}

export interface DashboardMetrics {
  rounds: TrainingRound[];
}

export interface PredictionInput {
  age: number;
  sex: number;
  cp: number;
  trestbps: number;
  chol: number;
  fbs: number;
  restecg: number;
  thalach: number;
  exang: number;
  oldpeak: number;
  slope: number;
}

export interface PredictionResult {
  risk_score: number;
  risk_level: string;
}

export async function registerHospital(data: {
  name: string;
  location: string;
  admin_email: string;
}, enrollmentCode: string): Promise<HospitalRegistration> {
  return (
    await api.post<HospitalRegistration>("/api/hospitals/register", data, {
      headers: { "X-Registration-Token": enrollmentCode },
    })
  ).data;
}

export async function loginHospital(data: {
  api_key: string;
}): Promise<LoginResponse> {
  return (await api.post<LoginResponse>("/api/hospitals/login", data)).data;
}

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  return (await api.get<DashboardMetrics>("/api/dashboard/metrics")).data;
}

export async function predictHeartDisease(
  data: PredictionInput,
): Promise<PredictionResult> {
  return (await api.post<PredictionResult>("/api/inference/predict", data)).data;
}

export function isUnauthorized(error: unknown): boolean {
  return axios.isAxiosError(error) && error.response?.status === 401;
}

export function apiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
  }
  return error instanceof Error ? error.message : fallback;
}

export default api;
