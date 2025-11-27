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
  // Password protection disabled for demo - will be enabled later
  // const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  // const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(true); // Always authenticated for demo
  const [settings, setSettings] = useState({
    temple_name: '',
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
  });

  const [moduleConfig, setModuleConfig] = useState({
    module_donations_enabled: true,
    module_sevas_enabled: true,
    module_inventory_enabled: true,
    module_assets_enabled: true,
    module_accounting_enabled: true,
    module_tender_enabled: true, // Enabled by default for demo
    module_hr_enabled: true, // HR & Salary Management
    module_panchang_enabled: true,
    module_reports_enabled: true,
    module_token_seva_enabled: true,
  });

  useEffect(() => {
    // Password protection disabled for demo - always fetch settings
    // const isAuth = sessionStorage.getItem('settings_authenticated') === 'true';
    // setAuthenticated(isAuth);
    
    // Always fetch settings for demo
    fetchSettings();
    fetchModuleConfig();
  }, []);

  const fetchModuleConfig = async () => {
    try {
      const response = await api.get('/api/v1/temples/modules/config');
      setModuleConfig(response.data);
    } catch (err) {
      console.error('Failed to fetch module configuration:', err);
    }
  };

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
        });
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      
      // Save module configuration
      await api.put('/api/v1/temples/modules/config', moduleConfig);
      
      // Save other settings (if API exists)
      // await api.put('/api/v1/temples/settings', settings);
      
      showSuccess('Settings saved successfully');
      
      // Refresh page to update menu
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to save settings');
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
          {/* Temple Information */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Temple Information
                </Typography>
                <TextField
                  fullWidth
                  label="Temple Name"
                  value={settings.temple_name}
                  onChange={(e) => setSettings({ ...settings, temple_name: e.target.value })}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Financial Year Start Month"
                  type="number"
                  value={settings.financial_year_start}
                  onChange={(e) => setSettings({ ...settings, financial_year_start: parseInt(e.target.value) })}
                  margin="normal"
                  inputProps={{ min: 1, max: 12 }}
                  helperText="1=January, 4=April (default)"
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Receipt Prefixes */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Receipt Prefixes
                </Typography>
                <TextField
                  fullWidth
                  label="Donation Receipt Prefix"
                  value={settings.receipt_prefix_donation}
                  onChange={(e) => setSettings({ ...settings, receipt_prefix_donation: e.target.value })}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Seva Receipt Prefix"
                  value={settings.receipt_prefix_seva}
                  onChange={(e) => setSettings({ ...settings, receipt_prefix_seva: e.target.value })}
                  margin="normal"
                />
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
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Module Configuration
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Enable or disable modules based on your temple's requirements. Disabled modules will be hidden from the menu.
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_donations_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_donations_enabled: e.target.checked })}
                        />
                      }
                      label="Donations Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_sevas_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_sevas_enabled: e.target.checked })}
                        />
                      }
                      label="Sevas Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_inventory_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_inventory_enabled: e.target.checked })}
                        />
                      }
                      label="Inventory Management"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_assets_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_assets_enabled: e.target.checked })}
                        />
                      }
                      label="Asset Management"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_accounting_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_accounting_enabled: e.target.checked })}
                        />
                      }
                      label="Accounting Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_tender_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_tender_enabled: e.target.checked })}
                        />
                      }
                      label="Tender Management (Optional)"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_hr_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_hr_enabled: e.target.checked })}
                        />
                      }
                      label="HR & Payroll Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_panchang_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_panchang_enabled: e.target.checked })}
                        />
                      }
                      label="Panchang Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_reports_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_reports_enabled: e.target.checked })}
                        />
                      }
                      label="Reports Module"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={moduleConfig.module_token_seva_enabled}
                          onChange={(e) => setModuleConfig({ ...moduleConfig, module_token_seva_enabled: e.target.checked })}
                        />
                      }
                      label="Token Seva Module"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Account Linking */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Account Linking
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Link donation categories and sevas to accounting accounts for proper categorization.
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => {
                    // Navigate to account linking page or show dialog
                    showSuccess('Account linking feature coming soon');
                  }}
                >
                  Link Accounts to Categories/Sevas
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          {/* Lock Settings button disabled for demo - will be enabled later */}
          {/* <Button
            variant="outlined"
            onClick={() => {
              setAuthenticated(false);
              sessionStorage.removeItem('settings_authenticated');
              navigate('/dashboard');
            }}
          >
            Lock Settings
          </Button> */}
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <SettingsIcon />}
          >
            Save Settings
          </Button>
        </Box>
      </Box>
    </Layout>
  );
}

export default Settings;
