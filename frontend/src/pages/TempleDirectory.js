import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import TempleHinduIcon from '@mui/icons-material/TempleHindu';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import AddBusinessIcon from '@mui/icons-material/AddBusiness';
import { Navigate, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';
import { readStoredUser } from '../utils/authStorage';
import { setActiveTempleId, emitActiveTempleChanged } from '../utils/activeTemple';

const getDisplayName = (temple) => temple?.name || temple?.trust_name || `Temple ${temple?.id || ''}`;
const getRequestId = (request) => String(request?.id || request?.request_id || '').trim();

function TempleDirectory() {
  const navigate = useNavigate();
  const { showError, showSuccess } = useNotification();
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [tenantActionKey, setTenantActionKey] = useState('');
  const [resendLoadingRequestId, setResendLoadingRequestId] = useState(null);
  const [temples, setTemples] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loadError, setLoadError] = useState('');
  const [approvalSummary, setApprovalSummary] = useState(null);
  const currentUser = useMemo(() => readStoredUser(), []);
  const isPlatformSuperAdmin = Boolean(currentUser.is_superuser) || currentUser.role === 'super_admin' || currentUser.system_role === 'super_admin';

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setLoadError('');
      const [templesResponse, requestsResponse] = await Promise.all([
        api.get('/api/v1/temples/'),
        api.get('/api/v1/onboarding-requests/'),
      ]);
      setTemples(Array.isArray(templesResponse.data) ? templesResponse.data : []);
      setRequests(Array.isArray(requestsResponse.data) ? requestsResponse.data : []);
    } catch (err) {
      const message = err.userMessage || err?.response?.data?.detail || 'Failed to load temple directory';
      setLoadError(message);
      showError(message);
    } finally {
      setLoading(false);
    }
  }, [showError]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDeactivateTemple = async (temple) => {
    const label = getDisplayName(temple);
    const confirmed = window.confirm(`Deactivate ${label}?\n\nYou can reactivate it later.`);
    if (!confirmed) {
      return;
    }

    const actionKey = `deactivate-${temple.id}`;
    try {
      setTenantActionKey(actionKey);
      await api.post(`/api/v1/temples/${temple.id}/deactivate`);
      showSuccess(`${label} deactivated`);
      await fetchData();
    } catch (err) {
      showError(err.userMessage || err?.response?.data?.detail || 'Failed to deactivate temple');
    } finally {
      setTenantActionKey('');
    }
  };

  const handleActivateTemple = async (temple) => {
    const label = getDisplayName(temple);
    const confirmed = window.confirm(`Activate ${label}?`);
    if (!confirmed) {
      return;
    }

    const actionKey = `activate-${temple.id}`;
    try {
      setTenantActionKey(actionKey);
      await api.post(`/api/v1/temples/${temple.id}/activate`);
      showSuccess(`${label} activated`);
      await fetchData();
    } catch (err) {
      showError(err.userMessage || err?.response?.data?.detail || 'Failed to activate temple');
    } finally {
      setTenantActionKey('');
    }
  };

  const handleRemoveTemple = async (temple) => {
    const label = getDisplayName(temple);
    const confirmation = window.prompt(`Type DELETE ${temple.id} to permanently remove ${label} and all related data.`);
    if (!confirmation) {
      return;
    }

    const actionKey = `remove-${temple.id}`;
    try {
      setTenantActionKey(actionKey);
      await api.delete(`/api/v1/temples/${temple.id}/remove`, {
        data: { confirm_text: confirmation },
      });
      showSuccess(`${label} removed completely`);
      await fetchData();
    } catch (err) {
      showError(err.userMessage || err?.response?.data?.detail || 'Failed to remove temple completely');
    } finally {
      setTenantActionKey('');
    }
  };

  const handleApprove = async (requestId) => {
    try {
      setActionLoadingId(requestId);
      const response = await api.post(`/api/v1/onboarding-requests/${requestId}/approve`, {});
      setApprovalSummary({ ...(response.data || {}), _action: 'approved' });
      showSuccess(`Approved onboarding request for ${response.data.admin_email}`);
      await fetchData();
    } catch (err) {
      showError(err.userMessage || 'Failed to approve onboarding request');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleReject = async (requestId) => {
    const reviewNotes = window.prompt('Enter the rejection reason for this onboarding request:');
    if (!reviewNotes || reviewNotes.trim().length < 3) {
      return;
    }

    try {
      setActionLoadingId(requestId);
      await api.post(`/api/v1/onboarding-requests/${requestId}/reject`, { review_notes: reviewNotes.trim() });
      showSuccess('Onboarding request rejected');
      await fetchData();
    } catch (err) {
      showError(err.userMessage || 'Failed to reject onboarding request');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleResendCredentials = async (request, temple) => {
    const requestId = getRequestId(request);
    if (!requestId) {
      showError('No approved onboarding request found for this temple.');
      return;
    }

    const templeLabel = getDisplayName(temple);
    const confirmed = window.confirm(`Resend onboarding email for ${templeLabel}?\n\nA new temporary password will be generated.`);
    if (!confirmed) {
      return;
    }

    try {
      setResendLoadingRequestId(requestId);
      const response = await api.post(`/api/v1/onboarding-requests/${requestId}/resend-credentials`, {});
      setApprovalSummary({ ...(response.data || {}), _action: 'resent' });
      if (response.data?.email_sent) {
        showSuccess(`Onboarding email re-sent to ${response.data.admin_email}`);
      } else {
        showError(response.data?.email_error || 'Email could not be sent. Share temporary password manually.');
      }
      await fetchData();
    } catch (err) {
      showError(err.userMessage || err?.response?.data?.detail || 'Failed to resend onboarding email');
    } finally {
      setResendLoadingRequestId(null);
    }
  };

  if (!isPlatformSuperAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  const activeTempleCount = temples.filter((temple) => temple.is_active !== false).length;
  const pendingRequests = requests.filter((request) => request.status === 'pending');
  const approvedRequests = requests.filter((request) => request.status === 'approved');
  const approvedRequestByTenant = approvedRequests.reduce((acc, request) => {
    const tenantKey = String(request?.approved_tenant_id || '').trim();
    if (tenantKey && !acc[tenantKey]) {
      acc[tenantKey] = request;
    }
    return acc;
  }, {});
  const demoTemples = temples.filter((temple) => Boolean(temple.platform_can_write));

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', md: 'center' }} spacing={2} sx={{ mb: 3 }}>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            <TempleHinduIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Temples / Trusts
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
            <Button variant="outlined" onClick={() => navigate('/settings')} startIcon={<AddBusinessIcon />}>
              Create Demo Tenant
            </Button>
            <Button variant="outlined" onClick={() => { setActiveTempleId(null); emitActiveTempleChanged(null); navigate('/settings'); }}>
              Open Platform Console
            </Button>
          </Stack>
        </Stack>

        {approvalSummary && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {approvalSummary._action === 'resent' ? 'Re-sent credentials for' : 'Approved request for'} {approvalSummary.admin_email}. Temporary password: <strong>{approvalSummary.temporary_password}</strong>. {approvalSummary.email_sent ? 'Onboarding email sent.' : approvalSummary.email_error ? `Onboarding email could not be sent (${approvalSummary.email_error}). Share the password manually.` : 'Share the password manually.'}
          </Alert>
        )}

        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(4, minmax(0, 1fr))' }, gap: 2, mb: 3 }}>
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
              <Typography variant="overline" color="text.secondary">Pending Approval</Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>{pendingRequests.length}</Typography>
            </CardContent>
          </Card>
          <Card sx={{ borderLeft: '5px solid #6A1B9A' }}>
            <CardContent>
              <Typography variant="overline" color="text.secondary">Access Model</Typography>
              <Typography variant="body1" sx={{ mt: 1 }}>Platform admins inspect every tenant, but only platform demo tenants are editable.</Typography>
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
          <Stack spacing={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                  <PendingActionsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Pending Temple / Trust Approvals
                </Typography>
                {pendingRequests.length === 0 ? (
                  <Alert severity="info">No pending registration requests at the moment.</Alert>
                ) : (
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 700 }}>Requested Temple / Trust</TableCell>
                          <TableCell sx={{ fontWeight: 700 }}>City</TableCell>
                          <TableCell sx={{ fontWeight: 700 }}>Requested Admin</TableCell>
                          <TableCell sx={{ fontWeight: 700 }}>Admin Email</TableCell>
                          <TableCell sx={{ fontWeight: 700 }}>Created</TableCell>
                          <TableCell sx={{ fontWeight: 700 }} align="right">Action</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {pendingRequests.map((request) => {
                          const requestId = getRequestId(request);
                          return (
                            <TableRow key={requestId} hover>
                              <TableCell sx={{ fontWeight: 600 }}>{request.temple_name || request.trust_name || 'Unnamed request'}</TableCell>
                              <TableCell>{request.city || '--'}</TableCell>
                              <TableCell>{request.admin_full_name}</TableCell>
                              <TableCell>{request.admin_email}</TableCell>
                              <TableCell>{request.created_at}</TableCell>
                              <TableCell align="right">
                                <Stack direction="row" spacing={1} justifyContent="flex-end">
                                  <Button size="small" variant="contained" disabled={actionLoadingId === requestId} onClick={() => handleApprove(requestId)}>
                                    {actionLoadingId === requestId ? 'Approving...' : 'Approve'}
                                  </Button>
                                  <Button size="small" variant="outlined" color="error" disabled={actionLoadingId === requestId} onClick={() => handleReject(requestId)}>
                                    Reject
                                  </Button>
                                </Stack>
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
                  Onboarded Temples / Trusts
                </Typography>
                <TableContainer component={Paper} variant="outlined">
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
                      {demoTemples.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={11}>
                            <Alert severity="info">No temples or trusts have been onboarded yet.</Alert>
                          </TableCell>
                        </TableRow>
                      ) : (
                        demoTemples.map((temple) => {
                          const tenantKey = String(temple?.tenant_id || '').trim();
                          const linkedApprovedRequest = approvedRequestByTenant[tenantKey];
                          const linkedRequestId = getRequestId(linkedApprovedRequest);
                          return (
                            <TableRow key={temple.id} hover>
                              <TableCell>{temple.id}</TableCell>
                              <TableCell sx={{ fontWeight: 600 }}>{getDisplayName(temple)}</TableCell>
                              <TableCell>{temple.trust_name || '--'}</TableCell>
                              <TableCell>{temple.primary_deity || '--'}</TableCell>
                              <TableCell>{temple.city || '--'}</TableCell>
                              <TableCell>{temple.state || '--'}</TableCell>
                              <TableCell>{temple.phone || '--'}</TableCell>
                              <TableCell>{temple.email || '--'}</TableCell>
                              <TableCell>
                                <Chip size="small" color={temple.is_active === false ? 'default' : 'success'} label={temple.is_active === false ? 'Inactive' : 'Active'} variant={temple.is_active === false ? 'outlined' : 'filled'} />
                              </TableCell>
                              <TableCell>
                                <Chip size="small" color={temple.platform_can_write ? 'warning' : 'default'} label={temple.platform_can_write ? 'Demo Editable' : 'Read-only'} variant={temple.platform_can_write ? 'filled' : 'outlined'} />
                              </TableCell>
                              <TableCell align="right">
                                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} justifyContent="flex-end">
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    disabled={!linkedRequestId || resendLoadingRequestId === linkedRequestId}
                                    onClick={() => handleResendCredentials(linkedApprovedRequest, temple)}
                                  >
                                    {resendLoadingRequestId === linkedRequestId ? 'Resending...' : 'Resend Email'}
                                  </Button>
                                  {temple.is_active === false ? (
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      color="success"
                                      disabled={tenantActionKey === `activate-${temple.id}`}
                                      onClick={() => handleActivateTemple(temple)}
                                    >
                                      {tenantActionKey === `activate-${temple.id}` ? 'Activating...' : 'Activate'}
                                    </Button>
                                  ) : (
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      color="warning"
                                      disabled={tenantActionKey === `deactivate-${temple.id}`}
                                      onClick={() => handleDeactivateTemple(temple)}
                                    >
                                      {tenantActionKey === `deactivate-${temple.id}` ? 'Deactivating...' : 'Deactivate'}
                                    </Button>
                                  )}
                                  <Button
                                    size="small"
                                    variant="outlined"
                                    color="error"
                                    disabled={tenantActionKey === `remove-${temple.id}`}
                                    onClick={() => handleRemoveTemple(temple)}
                                  >
                                    {tenantActionKey === `remove-${temple.id}` ? 'Removing...' : 'Remove Completely'}
                                  </Button>
                                </Stack>
                              </TableCell>
                            </TableRow>
                          );
                        })
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Stack>
        )}
      </Box>
    </Layout>
  );
}

export default TempleDirectory;
