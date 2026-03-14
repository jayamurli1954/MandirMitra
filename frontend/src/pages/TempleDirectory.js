import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import TempleHinduIcon from '@mui/icons-material/TempleHindu';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { Navigate, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';
import { readStoredUser } from '../utils/authStorage';

const ACTIVE_TEMPLE_STORAGE_KEY = 'active_temple_id_v1';

const getDisplayName = (temple) => temple?.name || temple?.trust_name || `Temple ${temple?.id || ''}`;

function TempleDirectory() {
  const navigate = useNavigate();
  const { showError } = useNotification();
  const [loading, setLoading] = useState(true);
  const [temples, setTemples] = useState([]);
  const [loadError, setLoadError] = useState('');
  const currentUser = useMemo(() => readStoredUser(), []);
  const isPlatformSuperAdmin = Boolean(currentUser.is_superuser) || currentUser.role === 'super_admin' || currentUser.system_role === 'super_admin';

  useEffect(() => {
    const fetchTemples = async () => {
      try {
        setLoading(true);
        setLoadError('');
        const response = await api.get('/api/v1/temples/');
        const templeList = Array.isArray(response.data) ? response.data : [];
        setTemples(templeList);
      } catch (err) {
        const message = err.userMessage || err?.response?.data?.detail || 'Failed to load onboarded temples and trusts';
        setLoadError(message);
        showError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchTemples();
  }, [showError]);

  const handleOpenTemple = (templeId) => {
    localStorage.setItem(ACTIVE_TEMPLE_STORAGE_KEY, String(templeId));
    window.dispatchEvent(new CustomEvent('active-temple-changed', {
      detail: { templeId },
    }));
    navigate('/settings');
  };

  if (!isPlatformSuperAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  const activeTempleCount = temples.filter((temple) => temple.is_active !== false).length;

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 3 }}>
          <TempleHinduIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Temples / Trusts
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, minmax(0, 1fr))' }, gap: 2, mb: 3 }}>
          <Card sx={{ borderLeft: '5px solid #FF9933' }}>
            <CardContent>
              <Typography variant="overline" color="text.secondary">Total Onboarded</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>{temples.length}</Typography>
            </CardContent>
          </Card>
          <Card sx={{ borderLeft: '5px solid #2E7D32' }}>
            <CardContent>
              <Typography variant="overline" color="text.secondary">Active</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>{activeTempleCount}</Typography>
            </CardContent>
          </Card>
          <Card sx={{ borderLeft: '5px solid #1565C0' }}>
            <CardContent>
              <Typography variant="overline" color="text.secondary">Access Model</Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>Platform admins can inspect every onboarded temple, but only demo temples marked editable can be changed.</Typography>
            </CardContent>
          </Card>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : loadError ? (
          <Alert severity="error">{loadError}</Alert>
        ) : (
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700 }}>ID</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Temple / Trust</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Trust Name</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Primary Deity</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>City</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>State</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Phone</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Email</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Platform Access</TableCell>
                  <TableCell sx={{ fontWeight: 700 }} align="right">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {temples.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={11}>
                      <Alert severity="info">No temples or trusts have been onboarded yet.</Alert>
                    </TableCell>
                  </TableRow>
                ) : (
                  temples.map((temple) => (
                    <TableRow key={temple.id} hover>
                      <TableCell>{temple.id}</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>{getDisplayName(temple)}</TableCell>
                      <TableCell>{temple.trust_name || '—'}</TableCell>
                      <TableCell>{temple.primary_deity || '—'}</TableCell>
                      <TableCell>{temple.city || '—'}</TableCell>
                      <TableCell>{temple.state || '—'}</TableCell>
                      <TableCell>{temple.phone || '—'}</TableCell>
                      <TableCell>{temple.email || '—'}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          color={temple.is_active === false ? 'default' : 'success'}
                          label={temple.is_active === false ? 'Inactive' : 'Active'}
                          variant={temple.is_active === false ? 'outlined' : 'filled'}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          color={temple.platform_can_write ? 'warning' : 'default'}
                          label={temple.platform_can_write ? 'Demo Editable' : 'Read-only'}
                          variant={temple.platform_can_write ? 'filled' : 'outlined'}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          size="small"
                          variant="outlined"
                          endIcon={<OpenInNewIcon />}
                          onClick={() => handleOpenTemple(temple.id)}
                        >
                          {temple.platform_can_write ? 'Open in Settings' : 'Open Read-only'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Layout>
  );
}

export default TempleDirectory;
