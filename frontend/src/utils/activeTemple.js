export const ACTIVE_TEMPLE_STORAGE_KEY = "active_temple_id_v1";
export const ACTIVE_TEMPLE_EVENT = "active-temple-changed";
export const ACTIVE_TEMPLE_HEADER = "X-Temple-Id";

export function getActiveTempleId() {
  const raw = localStorage.getItem(ACTIVE_TEMPLE_STORAGE_KEY);
  if (!raw) {
    return null;
  }
  const parsed = Number.parseInt(raw, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export function setActiveTempleId(templeId) {
  if (!templeId) {
    localStorage.removeItem(ACTIVE_TEMPLE_STORAGE_KEY);
    return;
  }
  localStorage.setItem(ACTIVE_TEMPLE_STORAGE_KEY, String(templeId));
}

export function emitActiveTempleChanged(templeId) {
  window.dispatchEvent(new CustomEvent(ACTIVE_TEMPLE_EVENT, {
    detail: { templeId },
  }));
}

export function buildActiveTempleHeaders(headers = {}) {
  const templeId = getActiveTempleId();
  if (!templeId) {
    return headers;
  }
  return {
    ...headers,
    [ACTIVE_TEMPLE_HEADER]: String(templeId),
  };
}
