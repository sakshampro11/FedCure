import axios from 'axios';

const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('fedcure_jwt');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const registerHospital = async (data: { name: string; location: string; admin_email: string }) => {
  const response = await api.post('/api/hospitals/register', data);
  return response.data;
};

export const loginHospital = async (data: { api_key: string }) => {
  const response = await api.post('/api/hospitals/login', data);
  return response.data;
};

export const getDashboardMetrics = async () => {
  const response = await api.get('/api/dashboard/metrics');
  return response.data;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const predictHeartDisease = async (data: any) => {
  const response = await api.post('/api/inference/predict', data);
  return response.data;
};

export default api;
