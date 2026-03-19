import { buildActiveTempleHeaders } from './activeTemple';

const LOCAL_API_BASE_URL = 'http://localhost:8000';
const PRODUCTION_FALLBACK_API_BASE_URL = (
  process.env.REACT_APP_FALLBACK_API_URL || process.env.REACT_APP_API_URL || 'https://mandirmitra-backend.onrender.com'
)
  .trim()
  .replace(/\/$/, '');

function isLocalHostname(hostname = '') {
  const host = String(hostname || '').toLowerCase();
  return host === 'localhost' || host === '127.0.0.1' || host === '::1';
}

function isLocalUrl(url = '') {
  try {
    const parsed = new URL(url);
    return isLocalHostname(parsed.hostname);
  } catch (_err) {
    return /^https?:\/\/(localhost|127\.0\.0\.1|::1)(:\d+)?$/i.test(String(url || '').trim());
  }
}

function isBrowserLocal() {
  if (typeof window === 'undefined') return false;
  return isLocalHostname(window.location.hostname);
}

export function getApiBaseUrl(options = {}) {
  const { preferDirect = false } = options;
  const configuredBaseUrl = (process.env.REACT_APP_API_URL || '').trim().replace(/\/$/, '');
  const browserLocal = isBrowserLocal();

  // Direct mode is used for explicit fallback attempts. In production-like hosts,
  // always route to a reachable public backend origin.
  if (preferDirect) {
    if (!browserLocal) {
      return PRODUCTION_FALLBACK_API_BASE_URL;
    }
    return configuredBaseUrl || LOCAL_API_BASE_URL;
  }

  if (configuredBaseUrl) {
    // Ignore localhost API URL when the app is served from non-localhost origins
    // (common accidental production build misconfiguration).
    if (!browserLocal && isLocalUrl(configuredBaseUrl)) {
      return PRODUCTION_FALLBACK_API_BASE_URL;
    }
    return configuredBaseUrl;
  }

  if (browserLocal) {
    return LOCAL_API_BASE_URL;
  }

  return PRODUCTION_FALLBACK_API_BASE_URL;
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
      const mergedHeaders = buildActiveTempleHeaders(init.headers || {});
      return await fetch(url, { ...init, headers: mergedHeaders, signal: controller.signal });
    } catch (error) {
      const message = String(error?.message || '').toLowerCase();
      if (error?.name === 'AbortError' || message.includes('aborted')) {
        lastError = new Error(
          'Request timed out while waiting for backend. The backend may be waking up; please retry in 30-60 seconds.'
        );
      } else {
        lastError = error;
      }
    } finally {
      window.clearTimeout(timer);
    }
  }

  throw lastError || new Error('Unable to reach backend');
}

