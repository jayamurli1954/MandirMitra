import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { fetchWithApiFallback } from '../utils/apiBaseUrl';
import { getAccessToken, readStoredUser, writeStoredUser } from '../utils/authStorage';

const SETUP_REDIRECT_EXEMPT_PATHS = new Set(['/profile']);

const readCurrentUser = () => readStoredUser();

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

function ProtectedRoute({ children }) {
  const token = getAccessToken();
  const location = useLocation();
  const [state, setState] = useState({ loading: true, redirectTo: null });

  useEffect(() => {
    if (!token) {
      setState({ loading: false, redirectTo: null });
      return;
    }

    let cancelled = false;

    const checkSetupStatus = async () => {
      try {
        const fallbackUser = readCurrentUser();
        const [setupResponse, currentUserResponse] = await Promise.all([
          fetchWithApiFallback('/api/v1/setup-wizard/status', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }, { timeoutMs: 12000 }),
          fetchWithApiFallback('/api/v1/users/me', {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }, { timeoutMs: 12000 }),
        ]);

        if (!setupResponse.ok) {
          throw new Error('Setup status unavailable');
        }

        const data = await setupResponse.json();
        let currentUser = fallbackUser;

        if (currentUserResponse.ok) {
          const currentUserData = await currentUserResponse.json();
          currentUser = normalizeCurrentUser(currentUserData, fallbackUser);
          writeStoredUser(currentUser);
        }

        const onWizardPage = location.pathname === '/setup-wizard';
        const isSetupRedirectExempt = SETUP_REDIRECT_EXEMPT_PATHS.has(location.pathname);
        const isPlatformSuperAdmin =
          Boolean(currentUser?.is_superuser)
          || currentUser?.system_role === 'super_admin'
          || currentUser?.role === 'super_admin';
        let redirectTo = null;

        if (data.force_setup && !onWizardPage && !isSetupRedirectExempt && !isPlatformSuperAdmin) {
          redirectTo = '/setup-wizard';
        } else if (onWizardPage && !data.can_manage_setup && !isPlatformSuperAdmin) {
          redirectTo = '/dashboard';
        }

        if (!cancelled) {
          setState({ loading: false, redirectTo });
        }
      } catch (error) {
        if (!cancelled) {
          setState({ loading: false, redirectTo: null });
        }
      }
    };

    checkSetupStatus();
    return () => {
      cancelled = true;
    };
  }, [token, location.pathname]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (state.loading) {
    return <div style={{ padding: 16 }}>Loading...</div>;
  }

  if (state.redirectTo && state.redirectTo !== location.pathname) {
    return <Navigate to={state.redirectTo} replace />;
  }

  return children;
}

export default ProtectedRoute;
