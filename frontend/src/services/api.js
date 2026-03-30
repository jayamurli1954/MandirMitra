import axios from 'axios';
import { getApiBaseUrl } from '../utils/apiBaseUrl';
import { buildActiveTempleHeaders } from '../utils/activeTemple';
import { clearAuthSession, getAccessToken } from '../utils/authStorage';
import { handleTenantInactive, isTenantInactiveMessage, isTenantInactivePayload } from '../utils/tenantInactive';

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
    const token = getAccessToken();
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
    const status = error.response?.status;
    const errorData = error.response?.data;

    if (status === 401) {
      clearAuthSession();
      window.location.href = '/login';
    }

    if (status === 403 && (isTenantInactivePayload(errorData) || isTenantInactiveMessage(errorData?.detail))) {
      handleTenantInactive(typeof errorData?.detail === 'string' ? errorData.detail : 'Tenant is inactive');
    }

    // Extract error message from response
    let errorMessage = 'An error occurred';
    if (errorData) {
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
