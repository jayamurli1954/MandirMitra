import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { fetchWithApiFallback } from '../utils/apiBaseUrl';
import { clearAuthSession, getAccessToken, readStoredUser, writeStoredUser, clearStoredUser } from '../utils/authStorage';

const LAYOUT_CACHE_TTL_MS = 2 * 60 * 1000;
const USER_PROFILE_CACHE_KEY = 'layout_user_profile_cache_v1';

const CurrentUserContext = createContext({
  user: {},
  loading: false,
  refreshUser: async () => ({}),
  clearUser: () => {},
});

const readCachedProfile = () => {
  try {
    const raw = sessionStorage.getItem(USER_PROFILE_CACHE_KEY);
    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object') {
      sessionStorage.removeItem(USER_PROFILE_CACHE_KEY);
      return null;
    }

    if (typeof parsed.expiresAt !== 'number' || Date.now() > parsed.expiresAt) {
      sessionStorage.removeItem(USER_PROFILE_CACHE_KEY);
      return null;
    }

    return parsed.value ?? null;
  } catch (error) {
    sessionStorage.removeItem(USER_PROFILE_CACHE_KEY);
    return null;
  }
};

const writeCachedProfile = (value, ttlMs = LAYOUT_CACHE_TTL_MS) => {
  try {
    sessionStorage.setItem(
      USER_PROFILE_CACHE_KEY,
      JSON.stringify({
        value,
        expiresAt: Date.now() + ttlMs,
      })
    );
  } catch (error) {
    // Ignore storage write failures.
  }
};

const normalizeCurrentUser = (userData, fallbackUser = {}) => ({
  ...fallbackUser,
  id: userData?.id ?? fallbackUser.id,
  email: userData?.email ?? fallbackUser.email,
  full_name: userData?.full_name ?? fallbackUser.full_name,
  name: userData?.full_name || userData?.email || fallbackUser.name,
  role: userData?.system_role || userData?.role || fallbackUser.role,
  system_role: userData?.system_role || userData?.role || fallbackUser.system_role,
  role_key: userData?.role_key ?? fallbackUser.role_key,
  role_label: userData?.role_label ?? fallbackUser.role_label,
  phone: userData?.phone ?? fallbackUser.phone ?? '',
  module_permissions: userData?.module_permissions || fallbackUser.module_permissions || {},
  action_permissions: userData?.action_permissions || fallbackUser.action_permissions || {},
  is_superuser: Boolean(userData?.is_superuser ?? fallbackUser.is_superuser),
});

export function CurrentUserProvider({ children }) {
  const [user, setUser] = useState(() => {
    const cachedProfile = readCachedProfile();
    if (cachedProfile && typeof cachedProfile === 'object') {
      return cachedProfile;
    }
    return readStoredUser();
  });
  const [loading, setLoading] = useState(() => Boolean(getAccessToken()));

  const applyUser = useCallback((nextUser) => {
    const normalized = normalizeCurrentUser(nextUser, readStoredUser());
    setUser(normalized);
    writeStoredUser(normalized);
    writeCachedProfile(normalized);
    return normalized;
  }, []);

  const clearUser = useCallback(() => {
    setUser({});
    setLoading(false);
    clearStoredUser();
    sessionStorage.removeItem(USER_PROFILE_CACHE_KEY);
  }, []);

  const refreshUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      clearUser();
      return {};
    }

    setLoading(true);
    try {
      const response = await fetchWithApiFallback('/api/v1/users/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }, { timeoutMs: 12000 });

      if (!response.ok) {
        throw new Error('Failed to load current user');
      }

      const data = await response.json();
      return applyUser(data);
    } finally {
      setLoading(false);
    }
  }, [applyUser, clearUser]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }

    refreshUser().catch((error) => {
      console.error('Failed to refresh current user', error);
      clearAuthSession();
      clearUser();
    });
  }, [clearUser, refreshUser]);

  useEffect(() => {
    const handleProfileUpdated = (event) => {
      if (event?.detail && typeof event.detail === 'object') {
        applyUser(event.detail);
        setLoading(false);
        return;
      }

      refreshUser().catch((error) => {
        console.error('Failed to refresh current user after profile update', error);
        clearAuthSession();
        clearUser();
      });
    };

    const handleAuthStateChanged = (event) => {
      if (event?.detail?.clear) {
        clearUser();
        return;
      }

      refreshUser().catch((error) => {
        console.error('Failed to refresh current user after auth state change', error);
        clearAuthSession();
        clearUser();
      });
    };

    window.addEventListener('user-profile-updated', handleProfileUpdated);
    window.addEventListener('auth-state-changed', handleAuthStateChanged);

    return () => {
      window.removeEventListener('user-profile-updated', handleProfileUpdated);
      window.removeEventListener('auth-state-changed', handleAuthStateChanged);
    };
  }, [applyUser, clearUser, refreshUser]);

  const value = useMemo(() => ({
    user,
    loading,
    refreshUser,
    clearUser,
  }), [clearUser, loading, refreshUser, user]);

  return (
    <CurrentUserContext.Provider value={value}>
      {children}
    </CurrentUserContext.Provider>
  );
}

export function useCurrentUser() {
  return useContext(CurrentUserContext);
}
