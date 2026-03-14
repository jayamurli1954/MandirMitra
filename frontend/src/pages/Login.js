import React, { useState } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Link,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { IconButton, InputAdornment } from '@mui/material';
import { fetchWithApiFallback } from '../utils/apiBaseUrl';
import { setAccessToken, writeStoredUser } from '../utils/authStorage';

const normalizeCurrentUser = (userData, email) => ({
  id: userData?.id,
  email: userData?.email || email,
  full_name: userData?.full_name || '',
  name: userData?.full_name || userData?.email || email.split('@')[0],
  role: userData?.system_role || userData?.role || 'temple_manager',
  system_role: userData?.system_role || userData?.role || 'temple_manager',
  role_key: userData?.role_key,
  role_label: userData?.role_label,
  phone: userData?.phone || '',
  module_permissions: userData?.module_permissions || {},
  action_permissions: userData?.action_permissions || {},
  is_superuser: Boolean(userData?.is_superuser),
});

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleClickShowPassword = () => setShowPassword(!showPassword);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      const response = await fetchWithApiFallback('/api/v1/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      }, { timeoutMs: 20000 });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      setAccessToken(data.access_token);

      const profileResponse = await fetchWithApiFallback('/api/v1/users/me', {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      }, { timeoutMs: 12000 });

      let currentUser = {
        email,
        name: email.split('@')[0],
        role: 'temple_manager',
        system_role: 'temple_manager',
        is_superuser: false,
        module_permissions: {},
        action_permissions: {},
      };

      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        currentUser = normalizeCurrentUser(profileData, email);
      }

      writeStoredUser(currentUser);
      window.dispatchEvent(new CustomEvent('user-profile-updated', { detail: currentUser }));
      window.dispatchEvent(new CustomEvent('auth-state-changed'));

      sessionStorage.setItem('showBrandIntroAfterLogin', '1');
      navigate('/brand-intro');
    } catch (err) {
      console.error('Login error:', err);
      if (err?.name === 'AbortError') {
        setError('Backend login request timed out. Please check whether the Render backend is awake and reachable.');
      } else if (err instanceof TypeError) {
        setError('Cannot connect to backend server. Please check the backend URL, Render service status, and CORS settings.');
      } else {
        setError(err.message || 'Login failed. Please check your credentials.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
            <LockOutlinedIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography component="h1" variant="h4" sx={{ fontWeight: 'bold' }}>
              {'\u0950\uFE0F MandirMitra'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Temple Management System
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              autoComplete="email"
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleClickShowPassword}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2, py: 1.5 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Sign In'}
            </Button>
            <Box sx={{ textAlign: 'right', mb: 2 }}>
              <Link
                component="button"
                type="button"
                variant="body2"
                onClick={() => navigate('/forgot-password')}
              >
                Forgot Password?
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default Login;
