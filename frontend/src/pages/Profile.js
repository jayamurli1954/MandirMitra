import React, { useEffect, useMemo, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Chip,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

const splitName = (fullName = '') => {
  const parts = String(fullName || '').trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) {
    return { firstName: '', lastName: '' };
  }
  if (parts.length === 1) {
    return { firstName: parts[0], lastName: '' };
  }
  return {
    firstName: parts[0],
    lastName: parts.slice(1).join(' '),
  };
};

function Profile() {
  const { showSuccess, showError } = useNotification();

  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  const [profile, setProfile] = useState({
    id: null,
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    role: '',
    isActive: true,
  });

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const fullName = useMemo(() => {
    return [profile.firstName, profile.lastName].filter(Boolean).join(' ').trim();
  }, [profile.firstName, profile.lastName]);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get('/api/v1/users/me');
        const data = response.data || {};
        const nameParts = splitName(data.full_name || '');

        setProfile({
          id: data.id || null,
          firstName: nameParts.firstName,
          lastName: nameParts.lastName,
          email: data.email || '',
          phone: data.phone || '',
          role: data.role_label || data.role || '',
          isActive: Boolean(data.is_active),
        });
      } catch (err) {
        showError(err.userMessage || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [showError]);

  const handleSaveProfile = async () => {
    if (!profile.id) {
      return;
    }

    if (!profile.firstName.trim()) {
      showError('First name is required');
      return;
    }

    try {
      setSavingProfile(true);

      const payload = {
        full_name: fullName,
        email: profile.email.trim(),
        phone: profile.phone.trim() || null,
      };

      const response = await api.put(`/api/v1/users/${profile.id}`, payload);
      const data = response.data || {};

      const normalizedUser = {
        ...(JSON.parse(localStorage.getItem('user') || '{}')),
        id: data.id,
        email: data.email,
        full_name: data.full_name,
        name: data.full_name || data.email,
        role: data.system_role || data.role,
        system_role: data.system_role || data.role,
        role_key: data.role_key,
        role_label: data.role_label,
        phone: data.phone || '',
        module_permissions: data.module_permissions || {},
        action_permissions: data.action_permissions || {},
        is_superuser: Boolean(data.is_superuser),
      };

      localStorage.setItem('user', JSON.stringify(normalizedUser));
      window.dispatchEvent(new CustomEvent('user-profile-updated', { detail: normalizedUser }));

      showSuccess('Profile updated successfully');
    } catch (err) {
      showError(err.userMessage || 'Failed to update profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async () => {
    if (!profile.id) {
      return;
    }

    if (!passwordForm.currentPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
      showError('Please fill all password fields');
      return;
    }

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      showError('New password and confirm password do not match');
      return;
    }

    try {
      setSavingPassword(true);
      await api.put(`/api/v1/users/${profile.id}`, {
        current_password: passwordForm.currentPassword,
        password: passwordForm.newPassword,
      });

      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });

      showSuccess('Password changed successfully');
    } catch (err) {
      showError(err.userMessage || 'Failed to change password');
    } finally {
      setSavingPassword(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '55vh' }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
          Profile
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={7}>
            <Card sx={{ borderLeft: '5px solid #FF9933' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <PersonIcon color="primary" />
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    Personal Details
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="First Name"
                      fullWidth
                      value={profile.firstName}
                      onChange={(e) => setProfile((prev) => ({ ...prev, firstName: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Last Name"
                      fullWidth
                      value={profile.lastName}
                      onChange={(e) => setProfile((prev) => ({ ...prev, lastName: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      label="Email Address"
                      type="email"
                      fullWidth
                      value={profile.email}
                      onChange={(e) => setProfile((prev) => ({ ...prev, email: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      label="Mobile Number"
                      fullWidth
                      value={profile.phone}
                      onChange={(e) => setProfile((prev) => ({ ...prev, phone: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip label={`Role: ${profile.role || 'user'}`} color="primary" variant="outlined" />
                      <Chip
                        label={profile.isActive ? 'Status: Active' : 'Status: Inactive'}
                        color={profile.isActive ? 'success' : 'default'}
                        variant="outlined"
                      />
                    </Box>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    onClick={handleSaveProfile}
                    disabled={savingProfile}
                    sx={{ bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A00' } }}
                  >
                    {savingProfile ? 'Saving...' : 'Save Profile'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={5}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <LockIcon color="primary" />
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    Change Password
                  </Typography>
                </Box>

                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      label="Current Password"
                      type="password"
                      fullWidth
                      value={passwordForm.currentPassword}
                      onChange={(e) => setPasswordForm((prev) => ({ ...prev, currentPassword: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      label="New Password"
                      type="password"
                      fullWidth
                      value={passwordForm.newPassword}
                      onChange={(e) => setPasswordForm((prev) => ({ ...prev, newPassword: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      label="Confirm New Password"
                      type="password"
                      fullWidth
                      value={passwordForm.confirmPassword}
                      onChange={(e) => setPasswordForm((prev) => ({ ...prev, confirmPassword: e.target.value }))}
                    />
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button
                    variant="contained"
                    onClick={handleChangePassword}
                    disabled={savingPassword}
                    sx={{ bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A00' } }}
                  >
                    {savingPassword ? 'Updating...' : 'Update Password'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
}

export default Profile;
