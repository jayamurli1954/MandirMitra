import React, { useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Grid,
  Paper,
  TextField,
  Typography,
  Link,
} from '@mui/material';
import TempleHinduIcon from '@mui/icons-material/TempleHindu';
import { useNavigate } from 'react-router-dom';
import { fetchWithApiFallback } from '../utils/apiBaseUrl';

const INITIAL_FORM = {
  temple_name: '',
  trust_name: '',
  temple_slug: '',
  primary_deity: 'Lord Ganesha',
  address: '',
  city: '',
  state: '',
  pincode: '',
  phone: '',
  email: '',
  admin_full_name: '',
  admin_email: '',
  admin_phone: '',
};

function TempleRegistration() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL_FORM);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');

    if (!form.temple_name.trim() && !form.trust_name.trim()) {
      setError('Fill Temple Name or Trust Name');
      return;
    }
    if (!form.admin_full_name.trim() || !form.admin_email.trim()) {
      setError('Temple admin name and email are required');
      return;
    }

    try {
      setLoading(true);
      const response = await fetchWithApiFallback('/api/v1/onboarding-requests/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      }, { timeoutMs: 20000 });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || 'Failed to submit registration request');
      }

      setSuccess('Registration request submitted successfully. The platform owner will review and approve your temple or trust onboarding.');
      setForm(INITIAL_FORM);
    } catch (err) {
      const message = String(err?.message || '').trim();
      const isNetworkError = /failed to fetch|networkerror|load failed/i.test(message);
      if (isNetworkError) {
        setError('Cannot connect to backend server right now. Please check backend URL/service status and retry.');
      } else {
        setError(message || 'Failed to submit registration request');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <Box sx={{ my: 6 }}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <TempleHinduIcon color="primary" />
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              New Temple / Trust Registration
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Submit your temple or trust details here. The platform owner will review the request and approve onboarding before login credentials are issued.
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

          <Box component="form" onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}><TextField fullWidth label="Temple Name" value={form.temple_name} onChange={(e) => updateField('temple_name', e.target.value)} /></Grid>
              <Grid item xs={12} md={6}><TextField fullWidth label="Trust Name" value={form.trust_name} onChange={(e) => updateField('trust_name', e.target.value)} /></Grid>
              <Grid item xs={12} md={6}><TextField fullWidth label="Temple Slug (optional)" value={form.temple_slug} onChange={(e) => updateField('temple_slug', e.target.value)} /></Grid>
              <Grid item xs={12} md={6}><TextField fullWidth label="Primary Deity" value={form.primary_deity} onChange={(e) => updateField('primary_deity', e.target.value)} /></Grid>
              <Grid item xs={12}><TextField fullWidth label="Address" value={form.address} onChange={(e) => updateField('address', e.target.value)} /></Grid>
              <Grid item xs={12} md={4}><TextField fullWidth label="City" value={form.city} onChange={(e) => updateField('city', e.target.value)} /></Grid>
              <Grid item xs={12} md={4}><TextField fullWidth label="State" value={form.state} onChange={(e) => updateField('state', e.target.value)} /></Grid>
              <Grid item xs={12} md={4}><TextField fullWidth label="PIN Code" value={form.pincode} onChange={(e) => updateField('pincode', e.target.value)} /></Grid>
              <Grid item xs={12} md={4}><TextField fullWidth label="Temple Phone" value={form.phone} onChange={(e) => updateField('phone', e.target.value)} /></Grid>
              <Grid item xs={12} md={4}><TextField fullWidth label="Temple Email" value={form.email} onChange={(e) => updateField('email', e.target.value)} /></Grid>
              <Grid item xs={12} md={4}><TextField fullWidth label="Primary Admin Phone" value={form.admin_phone} onChange={(e) => updateField('admin_phone', e.target.value)} /></Grid>
              <Grid item xs={12} md={6}><TextField fullWidth label="Primary Admin Full Name" value={form.admin_full_name} onChange={(e) => updateField('admin_full_name', e.target.value)} /></Grid>
              <Grid item xs={12} md={6}><TextField fullWidth label="Primary Admin Email" value={form.admin_email} onChange={(e) => updateField('admin_email', e.target.value)} /></Grid>
            </Grid>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 3, gap: 2, flexWrap: 'wrap' }}>
              <Link component="button" type="button" variant="body2" onClick={() => navigate('/login')}>
                Back to Login
              </Link>
              <Button type="submit" variant="contained" disabled={loading} sx={{ minWidth: 220 }}>
                {loading ? <CircularProgress size={24} /> : 'Submit Registration'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default TempleRegistration;

