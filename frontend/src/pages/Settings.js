import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Divider,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import LockIcon from '@mui/icons-material/Lock';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

function Settings() {
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [currentUser] = useState(() => JSON.parse(localStorage.getItem('user') || '{}'));
  const [backupStatus, setBackupStatus] = useState(null);
  const [backupLoading, setBackupLoading] = useState(false);
  const [manualBackupLoading, setManualBackupLoading] = useState(false);
  const [onboardingLoading, setOnboardingLoading] = useState(false);
  const [onboarding, setOnboarding] = useState({
    temple_name: '',
    trust_name: '',
    temple_slug: '',
    primary_deity: 'Lord Ganesha',
    city: '',
    state: '',
    phone: '',
    email: '',
    admin_full_name: '',
    admin_email: '',
    admin_password: '',
  });
  // Password protection disabled for demo - will be enabled later
  // const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  // const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(true); // Always authenticated for demo
  const [settings, setSettings] = useState({
    temple_name: '',
    name_kannada: '',
    name_sanskrit: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    phone: '',
    email: '',
    website: '',
    financial_year_start: 4,
    receipt_prefix_donation: 'DON',
    receipt_prefix_seva: 'SEVA',
    sms_enabled: false,
    sms_reminder_days: 7,
    email_enabled: false,
    // GST (Optional)
    gst_applicable: false,
    gstin: '',
    gst_registration_date: '',
    // FCRA (Optional)
    fcra_applicable: false,
    fcra_registration_number: '',
    fcra_valid_from: '',
    fcra_valid_to: '',
    // Modules
    module_donations_enabled: true,
    module_sevas_enabled: true,
    module_inventory_enabled: false,
    module_assets_enabled: false,
    module_hr_enabled: false,
    module_hundi_enabled: false,
    module_accounting_enabled: true,
    module_panchang_enabled: true,
    logo_url: '',
    banner_url: '',
  });

  useEffect(() => {
    // Password protection disabled for demo - always fetch settings
    // const isAuth = sessionStorage.getItem('settings_authenticated') === 'true';
    // setAuthenticated(isAuth);

    // Always fetch settings for demo
    fetchSettings();
    fetchBackupStatus();
  }, []);

  // Password protection disabled for demo - will be enabled later
  // const handlePasswordSubmit = () => {
  //   // Check if user is main admin
  //   const user = JSON.parse(localStorage.getItem('user') || '{}');
  //   
  //   // Allow admin, super_admin, or superuser roles
  //   const isAdmin = user.role === 'admin' || user.role === 'super_admin' || user.is_superuser === true;
  //   
  //   if (isAdmin && password === 'admin123') { // Default password - should be configurable
  //     setAuthenticated(true);
  //     sessionStorage.setItem('settings_authenticated', 'true');
  //     setPasswordDialogOpen(false);
  //     setPassword('');
  //     fetchSettings();
  //     showSuccess('Settings unlocked');
  //   } else {
  //     showError('Invalid password. Only main admin can access settings.');
  //     setPassword('');
  //   }
  // };

  const fetchSettings = async () => {
    try {
      setLoading(true);
      // Fetch temple settings
      const response = await api.get('/api/v1/temples/');
      if (response.data && response.data.length > 0) {
        const temple = response.data[0];
        setSettings({
          temple_name: temple.name || '',
          name_kannada: temple.name_kannada || '',
          name_sanskrit: temple.name_sanskrit || '',
          address: temple.address || '',
          city: temple.city || '',
          state: temple.state || '',
          pincode: temple.pincode || '',
          phone: temple.phone || '',
          email: temple.email || '',
          website: temple.website || '',
          financial_year_start: temple.financial_year_start_month || 4,
          receipt_prefix_donation: temple.receipt_prefix_donation || 'DON',
          receipt_prefix_seva: temple.receipt_prefix_seva || 'SEVA',
          sms_enabled: false, // Will be fetched from settings table
          sms_reminder_days: 7,
          email_enabled: false,
          // GST
          gst_applicable: temple.gst_applicable || false,
          gstin: temple.gstin || '',
          gst_registration_date: temple.gst_registration_date || '',
          // FCRA
          fcra_applicable: temple.fcra_applicable || false,
          fcra_registration_number: temple.fcra_registration_number || '',
          fcra_valid_from: temple.fcra_valid_from || '',
          fcra_valid_to: temple.fcra_valid_to || '',
          // Modules
          module_donations_enabled: temple.module_donations_enabled !== undefined ? temple.module_donations_enabled : true,
          module_sevas_enabled: temple.module_sevas_enabled !== undefined ? temple.module_sevas_enabled : true,
          module_inventory_enabled: temple.module_inventory_enabled !== undefined ? temple.module_inventory_enabled : false,
          module_assets_enabled: temple.module_assets_enabled !== undefined ? temple.module_assets_enabled : false,
          module_hr_enabled: temple.module_hr_enabled !== undefined ? temple.module_hr_enabled : false,
          module_hundi_enabled: temple.module_hundi_enabled !== undefined ? temple.module_hundi_enabled : false,
          module_accounting_enabled: temple.module_accounting_enabled !== undefined ? temple.module_accounting_enabled : true,
          module_panchang_enabled: temple.module_panchang_enabled !== undefined ? temple.module_panchang_enabled : true,
          logo_url: temple.logo_url || '',
          banner_url: temple.banner_url || '',
        });
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBackupStatus = async () => {
    const canAccessBackups = ['admin', 'super_admin', 'temple_manager'].includes(currentUser.role) || Boolean(currentUser.is_superuser);
    if (!canAccessBackups) return;

    try {
      setBackupLoading(true);
      const response = await api.get('/api/v1/backup-restore/status');
      setBackupStatus(response.data);
    } catch (err) {
      console.error('Failed to load backup status:', err);
    } finally {
      setBackupLoading(false);
    }
  };

  const handleManualBackup = async () => {
    try {
      setManualBackupLoading(true);
      const response = await api.post('/api/v1/backup-restore/backup');
      showSuccess(`Backup created: ${response.data.backup_file}`);
      await fetchBackupStatus();
    } catch (err) {
      showError(err?.response?.data?.detail || 'Failed to create backup');
    } finally {
      setManualBackupLoading(false);
    }
  };

  const handleOnboardingSubmit = async () => {
    const resolvedTempleName = (onboarding.temple_name || '').trim();
    const resolvedTrustName = (onboarding.trust_name || '').trim();
    if (!resolvedTempleName && !resolvedTrustName) {
      showError('Fill Temple Name or Trust Name');
      return;
    }
    if (!(onboarding.admin_full_name || '').trim()) {
      showError('Admin Full Name is required');
      return;
    }
    if (!(onboarding.admin_email || '').trim()) {
      showError('Admin Email is required');
      return;
    }
    if ((onboarding.admin_password || '').trim().length < 8) {
      showError('Admin Password must be at least 8 characters');
      return;
    }

    try {
      setOnboardingLoading(true);
      const payload = {
        temple_name: resolvedTempleName || null,
        trust_name: resolvedTrustName || null,
        temple_slug: onboarding.temple_slug || null,
        primary_deity: onboarding.primary_deity || null,
        city: onboarding.city || null,
        state: onboarding.state || null,
        phone: onboarding.phone || null,
        email: onboarding.email || null,
        admin_full_name: onboarding.admin_full_name,
        admin_email: onboarding.admin_email,
        admin_password: onboarding.admin_password,
      };
      const response = await api.post('/api/v1/temples/onboard', payload);
      showSuccess(`Onboarded ${response.data.temple_name} with admin ${response.data.admin_email}`);
      setOnboarding({
            temple_name: '',
        trust_name: '',
        temple_slug: '',
        primary_deity: 'Lord Ganesha',
        city: '',
        state: '',
        phone: '',
        email: '',
        admin_full_name: '',
        admin_email: '',
        admin_password: '',
      });
    } catch (err) {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail) && detail.length > 0) {
        showError(detail[0]?.msg || 'Failed to onboard temple/trust');
      } else if (typeof detail === 'string' && detail.trim()) {
        showError(detail);
      } else {
        showError('Failed to onboard temple/trust');
      }
    } finally {
      setOnboardingLoading(false);
    }
  };

  const handleFileUpload = async (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await api.post(`/api/v1/temples/upload?media_type=${type}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data && response.data.url) {
        setSettings({ ...settings, [`${type}_url`]: response.data.url });
        showSuccess(`${type.charAt(0).toUpperCase() + type.slice(1)} uploaded successfully`);
      }
    } catch (err) {
      console.error('Upload failed:', err);
      showError('Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);

      // 1. Save module configuration
      const moduleConfig = {
        module_donations_enabled: settings.module_donations_enabled,
        module_sevas_enabled: settings.module_sevas_enabled,
        module_inventory_enabled: settings.module_inventory_enabled,
        module_assets_enabled: settings.module_assets_enabled,
        module_hr_enabled: settings.module_hr_enabled,
        module_hundi_enabled: settings.module_hundi_enabled,
        module_accounting_enabled: settings.module_accounting_enabled,
        module_panchang_enabled: settings.module_panchang_enabled,
      };

      await api.put('/api/v1/temples/modules/config', moduleConfig);

      // 2. Save general temple information
      const financialYearStartMonth = Number.parseInt(settings.financial_year_start, 10);

      const templeInfo = {
        name: settings.temple_name,
        name_kannada: settings.name_kannada,
        name_sanskrit: settings.name_sanskrit,
        address: settings.address,
        city: settings.city,
        state: settings.state,
        pincode: settings.pincode,
        phone: settings.phone,
        email: settings.email,
        website: settings.website,
        ...(Number.isNaN(financialYearStartMonth) ? {} : { financial_year_start_month: financialYearStartMonth }),
        receipt_prefix_donation: settings.receipt_prefix_donation,
        receipt_prefix_seva: settings.receipt_prefix_seva,
        gst_applicable: settings.gst_applicable,
        gstin: settings.gstin,
        gst_registration_date: settings.gst_registration_date,
        fcra_applicable: settings.fcra_applicable,
        fcra_registration_number: settings.fcra_registration_number,
        fcra_valid_from: settings.fcra_valid_from,
        fcra_valid_to: settings.fcra_valid_to,
        logo_url: settings.logo_url,
        banner_url: settings.banner_url,
      };

      await api.put('/api/v1/temples/current', templeInfo);

      // 3. Refresh context
      await fetchSettings();

      window.dispatchEvent(new CustomEvent('module-config-updated', {
        detail: { ...moduleConfig, ...templeInfo },
      }));

      showSuccess('Settings saved successfully.');
    } catch (err) {
      console.error('Failed to save settings:', err);
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        const firstMsg = detail[0]?.msg;
        showError(firstMsg || 'Failed to save settings');
      } else if (typeof detail === 'string' && detail.trim()) {
        showError(detail);
      } else {
        showError('Failed to save settings');
      }
    } finally {
      setLoading(false);
    }
  };

  // Password protection disabled for demo - will be enabled later
  // if (!authenticated) {
  //   return (
  //     <Layout>
  //       <Dialog open={true} onClose={() => navigate('/dashboard')}>
  //         <DialogTitle>
  //           <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
  //             <LockIcon />
  //             Settings Password Required
  //           </Box>
  //         </DialogTitle>
  //         <DialogContent>
  //           <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
  //             Settings page is password protected. Only main admin can access.
  //           </Typography>
  //           <TextField
  //             fullWidth
  //             type="password"
  //             label="Enter Password"
  //             value={password}
  //             onChange={(e) => setPassword(e.target.value)}
  //             onKeyPress={(e) => {
  //               if (e.key === 'Enter') {
  //                 handlePasswordSubmit();
  //               }
  //             }}
  //             autoFocus
  //           />
  //         </DialogContent>
  //         <DialogActions>
  //           <Button onClick={() => navigate('/dashboard')}>Cancel</Button>
  //           <Button variant="contained" onClick={handlePasswordSubmit}>
  //             Unlock
  //           </Button>
  //         </DialogActions>
  //       </Dialog>
  //     </Layout>
  //   );
  // }

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Settings
        </Typography>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        <Grid container spacing={3} sx={{ mt: 2 }}>
          {(['admin', 'super_admin', 'temple_manager'].includes(currentUser.role) || currentUser.is_superuser) && (
            <Grid item xs={12}>
              <Card sx={{ borderLeft: '5px solid #1565C0' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Temple / Trust Onboarding
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Create a new temple or trust and assign its concerned temple admin in one step. Fill Temple Name or Trust Name. If both are filled, the top banner will show Temple Name.
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth label="Temple Name" helperText="Shown in top banner if filled. Required only when Trust Name is blank." value={onboarding.temple_name} onChange={(e) => setOnboarding({ ...onboarding, temple_name: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth label="Trust Name" helperText="Used in top banner when Temple Name is blank." value={onboarding.trust_name} onChange={(e) => setOnboarding({ ...onboarding, trust_name: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth label="Temple Slug" value={onboarding.temple_slug} onChange={(e) => setOnboarding({ ...onboarding, temple_slug: e.target.value })} helperText="Optional unique URL slug" />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField fullWidth label="Primary Deity" value={onboarding.primary_deity} onChange={(e) => setOnboarding({ ...onboarding, primary_deity: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField fullWidth label="City" value={onboarding.city} onChange={(e) => setOnboarding({ ...onboarding, city: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField fullWidth label="State" value={onboarding.state} onChange={(e) => setOnboarding({ ...onboarding, state: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <TextField fullWidth label="Temple Phone" value={onboarding.phone} onChange={(e) => setOnboarding({ ...onboarding, phone: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth label="Temple Email" value={onboarding.email} onChange={(e) => setOnboarding({ ...onboarding, email: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth label="Admin Full Name" value={onboarding.admin_full_name} onChange={(e) => setOnboarding({ ...onboarding, admin_full_name: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth label="Admin Email" value={onboarding.admin_email} onChange={(e) => setOnboarding({ ...onboarding, admin_email: e.target.value })} />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField fullWidth type="password" label="Admin Password" value={onboarding.admin_password} onChange={(e) => setOnboarding({ ...onboarding, admin_password: e.target.value })} />
                    </Grid>
                  </Grid>
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button variant="contained" onClick={handleOnboardingSubmit} disabled={onboardingLoading}>
                      {onboardingLoading ? 'Creating...' : 'Create Temple & Admin'}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {(['admin', 'super_admin', 'temple_manager'].includes(currentUser.role) || currentUser.is_superuser) && (
            <Grid item xs={12}>
              <Card sx={{ borderLeft: '5px solid #2E7D32' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="primary">
                    Backup Management
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Automatic local backups run every 30 minutes and only the latest 5 automated backups are retained. Manual backup is available below.
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
                    <Paper variant="outlined" sx={{ p: 2, minWidth: 220 }}>
                      <Typography variant="caption" color="text.secondary">Backup Path</Typography>
                      <Typography variant="body2">{backupStatus?.backup_directory || 'Loading...'}</Typography>
                    </Paper>
                    <Paper variant="outlined" sx={{ p: 2, minWidth: 180 }}>
                      <Typography variant="caption" color="text.secondary">Auto Backup</Typography>
                      <Typography variant="body2">Every {backupStatus?.auto_backup_interval_minutes || 30} minutes</Typography>
                    </Paper>
                    <Paper variant="outlined" sx={{ p: 2, minWidth: 180 }}>
                      <Typography variant="caption" color="text.secondary">Retention</Typography>
                      <Typography variant="body2">Latest {backupStatus?.auto_backup_keep_count || 5} auto backups</Typography>
                    </Paper>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                    <Button variant="contained" onClick={handleManualBackup} disabled={manualBackupLoading || backupLoading}>
                      {manualBackupLoading ? 'Creating Backup...' : 'Manual Backup'}
                    </Button>
                    <Button variant="outlined" onClick={fetchBackupStatus} disabled={backupLoading}>
                      {backupLoading ? 'Refreshing...' : 'Refresh Backup List'}
                    </Button>
                  </Box>
                  <Box sx={{ mt: 2 }}>
                    {(backupStatus?.backup_files || []).slice(0, 5).map((backupFile) => (
                      <Paper key={backupFile.filename} variant="outlined" sx={{ p: 1.5, mb: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {backupFile.filename.includes('_auto_') ? 'Auto Backup' : 'Manual Backup'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {backupFile.filename}
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          {backupFile.created_at} | {backupFile.size_mb} MB
                        </Typography>
                      </Paper>
                    ))}
                    {!backupLoading && (!backupStatus?.backup_files || backupStatus.backup_files.length === 0) && (
                      <Alert severity="info" sx={{ mt: 1 }}>No backups found yet.</Alert>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Temple Identity */}
          <Grid item xs={12}>
            <Card sx={{ borderLeft: '5px solid #FF9933' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  Temple Identity
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Display Name (English)"
                      value={settings.temple_name}
                      onChange={(e) => setSettings({ ...settings, temple_name: e.target.value })}
                      margin="normal"
                      required
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Temple Name (Kannada)"
                      value={settings.name_kannada}
                      onChange={(e) => setSettings({ ...settings, name_kannada: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Temple Name (Sanskrit)"
                      value={settings.name_sanskrit}
                      onChange={(e) => setSettings({ ...settings, name_sanskrit: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Address"
                      multiline
                      rows={2}
                      value={settings.address}
                      onChange={(e) => setSettings({ ...settings, address: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <TextField
                      fullWidth
                      label="City"
                      value={settings.city}
                      onChange={(e) => setSettings({ ...settings, city: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <TextField
                      fullWidth
                      label="Pincode"
                      value={settings.pincode}
                      onChange={(e) => setSettings({ ...settings, pincode: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={settings.phone}
                      onChange={(e) => setSettings({ ...settings, phone: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Email"
                      value={settings.email}
                      onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Website"
                      value={settings.website}
                      onChange={(e) => setSettings({ ...settings, website: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Branding & Images */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Branding & Images
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>Temple Logo</Typography>
                    <Box sx={{
                      mb: 2,
                      p: 2,
                      border: '1px dashed #ccc',
                      borderRadius: 1,
                      textAlign: 'center',
                      minHeight: 120,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: '#fafafa'
                    }}>
                      {settings.logo_url ? (
                        <img src={settings.logo_url} alt="Logo" style={{ maxHeight: 100, maxWidth: '100%' }} />
                      ) : (
                        <Typography variant="body2" color="text.secondary">No logo uploaded</Typography>
                      )}
                    </Box>
                    <Button variant="outlined" component="label" fullWidth>
                      Upload Logo
                      <input type="file" hidden accept="image/*" onChange={(e) => handleFileUpload(e, 'logo')} />
                    </Button>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>Temple Banner</Typography>
                    <Box sx={{
                      mb: 2,
                      p: 2,
                      border: '1px dashed #ccc',
                      borderRadius: 1,
                      textAlign: 'center',
                      minHeight: 120,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: '#fafafa'
                    }}>
                      {settings.banner_url ? (
                        <img src={settings.banner_url} alt="Banner" style={{ maxHeight: 100, maxWidth: '100%' }} />
                      ) : (
                        <Typography variant="body2" color="text.secondary">No banner uploaded</Typography>
                      )}
                    </Box>
                    <Button variant="outlined" component="label" fullWidth>
                      Upload Banner
                      <input type="file" hidden accept="image/*" onChange={(e) => handleFileUpload(e, 'banner')} />
                    </Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Financial & Receipt Configuration */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Financial & Receipt Configuration
                </Typography>
                <TextField
                  fullWidth
                  select
                  label="Financial Year Start"
                  value={settings.financial_year_start}
                  onChange={(e) => setSettings({ ...settings, financial_year_start: e.target.value })}
                  margin="normal"
                  SelectProps={{ native: true }}
                  helperText="Select which month your financial year starts in"
                >
                  <option value={1}>January (Calendar Year)</option>
                  <option value={4}>April (Indian Fiscal Year)</option>
                </TextField>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Donation Receipt Prefix"
                      value={settings.receipt_prefix_donation}
                      onChange={(e) => setSettings({ ...settings, receipt_prefix_donation: e.target.value })}
                      margin="normal"
                      placeholder="e.g., DON"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Seva Receipt Prefix"
                      value={settings.receipt_prefix_seva}
                      onChange={(e) => setSettings({ ...settings, receipt_prefix_seva: e.target.value })}
                      margin="normal"
                      placeholder="e.g., SEVA"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* SMS Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  SMS Reminder Settings
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.sms_enabled}
                      onChange={(e) => setSettings({ ...settings, sms_enabled: e.target.checked })}
                    />
                  }
                  label="Enable SMS Reminders"
                />
                {settings.sms_enabled && (
                  <TextField
                    fullWidth
                    label="Reminder Days Before Seva"
                    type="number"
                    value={settings.sms_reminder_days}
                    onChange={(e) => setSettings({ ...settings, sms_reminder_days: parseInt(e.target.value) })}
                    margin="normal"
                    inputProps={{ min: 1, max: 30 }}
                    helperText="Send reminder X days before seva date (default: 7 days)"
                  />
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Email Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Email Settings
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.email_enabled}
                      onChange={(e) => setSettings({ ...settings, email_enabled: e.target.checked })}
                    />
                  }
                  label="Enable Email Notifications"
                />
              </CardContent>
            </Card>
          </Grid>

          {/* GST Settings (Optional) */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  GST Registration (Optional)
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.gst_applicable}
                      onChange={(e) => setSettings({ ...settings, gst_applicable: e.target.checked })}
                    />
                  }
                  label="GST Applicable"
                />
                {settings.gst_applicable && (
                  <>
                    <TextField
                      fullWidth
                      label="GSTIN"
                      value={settings.gstin}
                      onChange={(e) => setSettings({ ...settings, gstin: e.target.value })}
                      margin="normal"
                      helperText="15-character GSTIN (e.g., 29AABCU1234A1Z5)"
                      inputProps={{ maxLength: 15 }}
                    />
                    <TextField
                      fullWidth
                      label="GST Registration Date"
                      type="date"
                      value={settings.gst_registration_date}
                      onChange={(e) => setSettings({ ...settings, gst_registration_date: e.target.value })}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* FCRA Settings (Optional) */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  FCRA Registration (Optional)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Foreign Contribution (Regulation) Act - Required only if receiving foreign donations
                </Typography>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.fcra_applicable}
                      onChange={(e) => setSettings({ ...settings, fcra_applicable: e.target.checked })}
                    />
                  }
                  label="FCRA Applicable"
                />
                {settings.fcra_applicable && (
                  <>
                    <TextField
                      fullWidth
                      label="FCRA Registration Number"
                      value={settings.fcra_registration_number}
                      onChange={(e) => setSettings({ ...settings, fcra_registration_number: e.target.value })}
                      margin="normal"
                    />
                    <TextField
                      fullWidth
                      label="FCRA Valid From"
                      type="date"
                      value={settings.fcra_valid_from}
                      onChange={(e) => setSettings({ ...settings, fcra_valid_from: e.target.value })}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                    <TextField
                      fullWidth
                      label="FCRA Valid To"
                      type="date"
                      value={settings.fcra_valid_to}
                      onChange={(e) => setSettings({ ...settings, fcra_valid_to: e.target.value })}
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Module Configuration */}
          <Grid item xs={12}>
            <Card sx={{ bgcolor: '#FFF8E1' }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  Module Configuration
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Enable or disable specific features for your temple. This will show/hide relevant menus in the sidebar.
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_donations_enabled}
                          onChange={(e) => setSettings({ ...settings, module_donations_enabled: e.target.checked })}
                        />
                      }
                      label="Donations Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_sevas_enabled}
                          onChange={(e) => setSettings({ ...settings, module_sevas_enabled: e.target.checked })}
                        />
                      }
                      label="Sevas Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_accounting_enabled}
                          onChange={(e) => setSettings({ ...settings, module_accounting_enabled: e.target.checked })}
                        />
                      }
                      label="Accounting Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_inventory_enabled}
                          onChange={(e) => setSettings({ ...settings, module_inventory_enabled: e.target.checked })}
                        />
                      }
                      label="Inventory Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_assets_enabled}
                          onChange={(e) => setSettings({ ...settings, module_assets_enabled: e.target.checked })}
                        />
                      }
                      label="Temple Assets Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_hr_enabled}
                          onChange={(e) => setSettings({ ...settings, module_hr_enabled: e.target.checked })}
                        />
                      }
                      label="HR & Salary Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_hundi_enabled}
                          onChange={(e) => setSettings({ ...settings, module_hundi_enabled: e.target.checked })}
                        />
                      }
                      label="Hundi Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.module_panchang_enabled}
                          onChange={(e) => setSettings({ ...settings, module_panchang_enabled: e.target.checked })}
                        />
                      }
                      label="Panchang Module"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SettingsIcon />}
            sx={{ bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A00' } }}
          >
            Save All Settings
          </Button>
        </Box>
      </Box>
    </Layout>
  );
}

export default Settings;
