import axios from 'axios';
import { getApiBaseUrl } from '../utils/apiBaseUrl';
import { buildActiveTempleHeaders } from '../utils/activeTemple';

const api = axios.create({
  baseURL: getApiBaseUrl({ preferDirect: true }),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 20000,
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    config.headers = buildActiveTempleHeaders(config.headers || {});
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // Extract error message from response
    let errorMessage = 'An error occurred';
    if (error.response?.data) {
      const errorData = error.response.data;
      if (errorData.error?.message) {
        errorMessage = errorData.error.message;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      } else if (errorData.detail) {
        errorMessage = errorData.detail;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    // Add error message to error object for easy access
    error.userMessage = errorMessage;
    
    return Promise.reject(error);
  }
);

export default api;

