import axios from 'axios';
import { useAppStore } from '@/lib/store';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token
api.interceptors.request.use((config) => {
  const token = useAppStore.getState().auth.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (data: any) => {
    const response = await api.post('/auth/login', data);
    return response.data;
  },
  register: async (data: any) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  loginWithGoogle: async (idToken: string) => {
    const response = await api.post('/auth/google', { id_token: idToken });
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const todayService = {
  getActions: async (data: {
    user_id: string;
    crop: string;
    location: string;
    sowing_date: string;
    language: string;
  }) => {
    const response = await api.post('/today/', data);
    return response.data;
  },
};

export const sellSmartService = {
  getMandiData: async (data: {
    crop: string;
    location: string;
    state: string;
    language: string;
  }) => {
    const response = await api.post('/sell-smart/', data);
    return response.data;
  },
};

export const chatService = {
  ask: async (data: {
    question: string;
    language: string;
    crop?: string;
    location?: string;
  }) => {
    const response = await api.post('/chat/', data);
    return response.data;
  },
};

export const schemeService = {
  getSchemes: async (data: {
    state: string;
    land_size: number;
    category: string;
    crop: string;
    language: string;
  }) => {
    const response = await api.post('/schemes/', data);
    return response.data;
  },
};

export const preferenceService = {
  updateLanguage: async (data: {
    user_id: string;
    language: string;
  }) => {
    const response = await api.post('/preferences/language', data);
    return response.data;
  },
  getLanguage: async (userId: string) => {
    const response = await api.get(`/preferences/${userId}/language`);
    return response.data;
  },
};

export default api;
