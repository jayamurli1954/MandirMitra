const LOCAL_API_BASE_URL = 'http://localhost:8000';

export function getApiBaseUrl() {
  const configuredBaseUrl = (process.env.REACT_APP_API_URL || '').trim().replace(/\/$/, '');
  if (configuredBaseUrl) {
    return configuredBaseUrl;
  }

  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return LOCAL_API_BASE_URL;
    }
  }

  return '';
}

export function buildApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${getApiBaseUrl()}${normalizedPath}`;
}
