const ACCESS_TOKEN_KEY = 'mm_access_token_v1';
const REFRESH_TOKEN_KEY = 'mm_refresh_token_v1';
const USER_KEY = 'mm_current_user_v1';
const LEGACY_TOKEN_KEY = 'token';
const LEGACY_REFRESH_TOKEN_KEY = 'refresh_token';
const LEGACY_USER_KEY = 'user';

const safeStorage = (storage) => {
  try {
    return storage;
  } catch (error) {
    return null;
  }
};

const session = () => safeStorage(window.sessionStorage);
const local = () => safeStorage(window.localStorage);

const moveLegacyValue = (legacyKey, nextKey) => {
  const localStore = local();
  const sessionStore = session();
  if (!localStore || !sessionStore) {
    return null;
  }

  const legacyValue = localStore.getItem(legacyKey);
  if (!legacyValue) {
    return null;
  }

  sessionStore.setItem(nextKey, legacyValue);
  localStore.removeItem(legacyKey);
  return legacyValue;
};

export const getAccessToken = () => {
  const sessionStore = session();
  if (sessionStore) {
    const current = sessionStore.getItem(ACCESS_TOKEN_KEY) || sessionStore.getItem(LEGACY_TOKEN_KEY);
    if (current) {
      if (!sessionStore.getItem(ACCESS_TOKEN_KEY)) {
        sessionStore.setItem(ACCESS_TOKEN_KEY, current);
        sessionStore.removeItem(LEGACY_TOKEN_KEY);
      }
      return current;
    }
  }

  return moveLegacyValue(LEGACY_TOKEN_KEY, ACCESS_TOKEN_KEY);
};

export const getRefreshToken = () => {
  const sessionStore = session();
  if (sessionStore) {
    const current = sessionStore.getItem(REFRESH_TOKEN_KEY) || sessionStore.getItem(LEGACY_REFRESH_TOKEN_KEY);
    if (current) {
      if (!sessionStore.getItem(REFRESH_TOKEN_KEY)) {
        sessionStore.setItem(REFRESH_TOKEN_KEY, current);
        sessionStore.removeItem(LEGACY_REFRESH_TOKEN_KEY);
      }
      return current;
    }
  }

  return moveLegacyValue(LEGACY_REFRESH_TOKEN_KEY, REFRESH_TOKEN_KEY);
};

export const hasAccessToken = () => Boolean(getAccessToken());

export const setAccessToken = (token) => {
  const sessionStore = session();
  const localStore = local();
  if (sessionStore) {
    sessionStore.setItem(ACCESS_TOKEN_KEY, token);
    sessionStore.removeItem(LEGACY_TOKEN_KEY);
  }
  if (localStore) {
    localStore.removeItem(LEGACY_TOKEN_KEY);
  }
};

export const setRefreshToken = (token) => {
  const sessionStore = session();
  const localStore = local();
  if (sessionStore) {
    if (token) {
      sessionStore.setItem(REFRESH_TOKEN_KEY, token);
    } else {
      sessionStore.removeItem(REFRESH_TOKEN_KEY);
    }
    sessionStore.removeItem(LEGACY_REFRESH_TOKEN_KEY);
  }
  if (localStore) {
    localStore.removeItem(LEGACY_REFRESH_TOKEN_KEY);
  }
};

export const readStoredUser = () => {
  const sessionStore = session();
  const sessionValue = sessionStore?.getItem(USER_KEY) || sessionStore?.getItem(LEGACY_USER_KEY);
  if (sessionValue) {
    try {
      const parsed = JSON.parse(sessionValue);
      if (!sessionStore?.getItem(USER_KEY)) {
        sessionStore?.setItem(USER_KEY, sessionValue);
        sessionStore?.removeItem(LEGACY_USER_KEY);
      }
      return parsed || {};
    } catch (error) {
      sessionStore?.removeItem(USER_KEY);
      sessionStore?.removeItem(LEGACY_USER_KEY);
    }
  }

  const migrated = moveLegacyValue(LEGACY_USER_KEY, USER_KEY);
  if (migrated) {
    try {
      return JSON.parse(migrated) || {};
    } catch (error) {
      sessionStore?.removeItem(USER_KEY);
    }
  }

  return {};
};

export const writeStoredUser = (user) => {
  const serialized = JSON.stringify(user || {});
  const sessionStore = session();
  const localStore = local();
  sessionStore?.setItem(USER_KEY, serialized);
  sessionStore?.removeItem(LEGACY_USER_KEY);
  localStore?.removeItem(LEGACY_USER_KEY);
};

export const clearStoredUser = () => {
  const sessionStore = session();
  const localStore = local();
  sessionStore?.removeItem(USER_KEY);
  sessionStore?.removeItem(LEGACY_USER_KEY);
  localStore?.removeItem(LEGACY_USER_KEY);
};

export const clearAuthSession = () => {
  const sessionStore = session();
  const localStore = local();
  sessionStore?.removeItem(ACCESS_TOKEN_KEY);
  sessionStore?.removeItem(LEGACY_TOKEN_KEY);
  sessionStore?.removeItem(REFRESH_TOKEN_KEY);
  sessionStore?.removeItem(LEGACY_REFRESH_TOKEN_KEY);
  sessionStore?.removeItem(USER_KEY);
  sessionStore?.removeItem(LEGACY_USER_KEY);
  localStore?.removeItem(LEGACY_TOKEN_KEY);
  localStore?.removeItem(LEGACY_REFRESH_TOKEN_KEY);
  localStore?.removeItem(LEGACY_USER_KEY);
};
