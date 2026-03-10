const LOCAL_API_BASE_URL = 'http://localhost:8000';
const PRODUCTION_FALLBACK_API_BASE_URL = (
  process.env.REACT_APP_FALLBACK_API_URL || 'https://mandirmitra-backend.onrender.com'
).trim().replace(/\/$/, '');

export function getApiBaseUrl(options = {}) {
  const { preferDirect = false } = options;
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

  if (preferDirect) {
    return PRODUCTION_FALLBACK_API_BASE_URL;
  }

  return '';
}

export function buildApiUrl(path, options = {}) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${getApiBaseUrl(options)}${normalizedPath}`;
}

export async function fetchWithApiFallback(path, init = {}, options = {}) {
  const { timeoutMs = 15000 } = options;
  const primaryUrl = buildApiUrl(path);
  const fallbackUrl = buildApiUrl(path, { preferDirect: true });
  const urls = primaryUrl === fallbackUrl ? [primaryUrl] : [primaryUrl, fallbackUrl];

  let lastError = null;
  for (const url of urls) {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeoutMs);

    try {
      return await fetch(url, { ...init, signal: controller.signal });
    } catch (error) {
      lastError = error;
    } finally {
      window.clearTimeout(timer);
    }
  }

  throw lastError || new Error('Unable to reach backend');
}
