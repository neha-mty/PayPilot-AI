/**
 * API service layer for PayPilot AI.
 * All backend communication goes through this module.
 * 
 * Uses Vite proxy in development: /api/* → http://localhost:8000/*
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('paypilot_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle 401 (token expired/invalid)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('paypilot_token');
      localStorage.removeItem('paypilot_user');
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// === Auth APIs ===
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
};

// === Budget APIs ===
export const budgetAPI = {
  list: () => api.get('/budget'),
  create: (data) => api.post('/budget', data),
};

// === Policy APIs ===
export const policyAPI = {
  get: () => api.get('/policies'),
  update: (data) => api.post('/policies', data),
};

// === Merchant & Product APIs ===
export const merchantAPI = {
  list: () => api.get('/merchants'),
  getProducts: (merchantId) => api.get(`/merchants/${merchantId}/products`),
};

// === AI Assistant APIs ===
export const assistantAPI = {
  chat: (message, agentType = 'universal') => api.post('/assistant/chat', { message, agent_type: agentType }),
};

// === Universal Marketplace APIs ===
export const marketplaceAPI = {
  search: (params = {}) => api.get('/marketplace/search', { params }),
  getCategories: () => api.get('/marketplace/categories'),
  getProviders: () => api.get('/marketplace/providers'),
  getProduct: (id) => api.get(`/marketplace/product/${id}`),
  detectIntent: (query) => api.post('/marketplace/detect-intent', { query }),
};

// === Payment Request APIs ===
export const paymentRequestAPI = {
  create: (data) => api.post('/payment-requests', data),
  get: (id) => api.get(`/payment-requests/${id}`),
  list: (status = null) => api.get('/payment-requests', { params: status ? { status } : {} }),
  approve: (id) => api.post(`/payment-requests/${id}/approve`),
  reject: (id) => api.post(`/payment-requests/${id}/reject`),
};

// === Payment APIs ===
export const paymentAPI = {
  create: (paymentRequestId) => api.post('/payments/create', { payment_request_id: paymentRequestId }),
  verify: (data) => api.post('/payments/verify', data),
};

// === Transaction APIs ===
export const transactionAPI = {
  list: () => api.get('/transactions'),
};

// === Audit Log APIs ===
export const auditAPI = {
  list: (params = {}) => api.get('/audit-logs', { params }),
};

// === Dashboard APIs ===
export const dashboardAPI = {
  summary: () => api.get('/dashboard/summary'),
};

export { api };
export default api;
