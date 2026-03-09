import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
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
        const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/v1/setup-wizard/status`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Setup status unavailable');
        }

        const data = await response.json();
        const onWizardPage = location.pathname === '/setup-wizard';
        let redirectTo = null;

        if (data.force_setup && !onWizardPage) {
          redirectTo = '/setup-wizard';
        } else if (onWizardPage && !data.can_manage_setup) {
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
