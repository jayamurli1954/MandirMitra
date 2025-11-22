import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Grid,
  Paper,
  Card,
  CardContent,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  InputAdornment,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import PeopleIcon from '@mui/icons-material/People';
import EventIcon from '@mui/icons-material/Event';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../components/Layout';
import PanchangDisplay from '../components/PanchangDisplay';
import api from '../services/api';

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState({
    todayDonations: 0,
    totalDevotees: 0,
    sevaBookings: 0,
    monthDonations: 0,
  });
  const [panchangData, setPanchangData] = useState(null);
  const [donationForm, setDonationForm] = useState({
    devotee_name: '',
    devotee_phone: '',
    amount: '',
    category: '',
    payment_mode: 'Cash',
    address: '',  // Street address
    pincode: '',
    city: '',
    state: '',
    country: 'India',
  });
  const [pincodeLoading, setPincodeLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchCategories();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      const [todayReportRes, allDonationsRes, devoteesRes, panchangSettingsRes, panchangDataRes] = await Promise.allSettled([
        api.get(`/api/v1/donations/report/daily?date=${today}`), // Use daily report endpoint
        api.get('/api/v1/donations?limit=1000'), // Get all donations to count devotees
        api.get('/api/v1/devotees'),
        api.get('/api/v1/panchang/display-settings/'),
        api.get('/api/v1/panchang/today'),
      ]);

      // Calculate today's donations from daily report
      let todayDonations = 0;
      if (todayReportRes.status === 'fulfilled' && todayReportRes.value.data) {
        todayDonations = todayReportRes.value.data.total || 0;
      } else if (todayReportRes.status === 'rejected') {
        // Fallback: try direct donations endpoint
        try {
          const fallbackRes = await api.get(`/api/v1/donations?date=${today}`);
          if (fallbackRes.data && Array.isArray(fallbackRes.data)) {
            todayDonations = fallbackRes.data.reduce((sum, d) => sum + (d.amount || 0), 0);
          }
        } catch (fallbackErr) {
          console.error('Fallback donations fetch failed:', fallbackErr);
        }
      }

      // Count unique devotees from ALL donations (not just today)
      let totalDevotees = 0;
      if (allDonationsRes.status === 'fulfilled' && allDonationsRes.value.data) {
        const uniqueDevotees = new Set();
        allDonationsRes.value.data.forEach(d => {
          if (d.devotee && d.devotee.phone) {
            uniqueDevotees.add(d.devotee.phone);
          } else if (d.devotee_phone) {
            uniqueDevotees.add(d.devotee_phone);
          }
        });
        totalDevotees = uniqueDevotees.size;
      }
      // Fallback: try to get from devotees API if available
      if (totalDevotees === 0 && devoteesRes.status === 'fulfilled' && devoteesRes.value.data) {
        totalDevotees = Array.isArray(devoteesRes.value.data) ? devoteesRes.value.data.length : 0;
      }

      // Fetch panchang settings and data
      let panchangSettings = null;
      let panchangData = null;
      
      if (panchangSettingsRes.status === 'fulfilled' && panchangSettingsRes.value.data) {
        panchangSettings = panchangSettingsRes.value.data;
      }
      
      if (panchangDataRes.status === 'fulfilled' && panchangDataRes.value.data) {
        panchangData = panchangDataRes.value.data;
      }
      
      // Set panchang data (merge settings if available)
      if (panchangData) {
        setPanchangData({
          ...panchangData,
          ...(panchangSettings || {})  // Settings override for display preferences
        });
      } else if (panchangSettings) {
        setPanchangData(panchangSettings);
      }

      // Calculate month donations
      const currentMonth = new Date().getMonth() + 1;
      const currentYear = new Date().getFullYear();
      let monthDonations = 0;
      try {
        const monthReportRes = await api.get(`/api/v1/donations/report/monthly?month=${currentMonth}&year=${currentYear}`);
        if (monthReportRes.data) {
          monthDonations = monthReportRes.data.total || 0;
        }
      } catch (monthErr) {
        console.error('Error fetching monthly report:', monthErr);
      }

      setStats({
        todayDonations,
        totalDevotees,
        sevaBookings: 0,
        monthDonations,
      });
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      // Don't use hardcoded values - show actual data or 0
      setStats({
        todayDonations: 0,
        totalDevotees: 0,
        sevaBookings: 0,
        monthDonations: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      setCategories([
        'General Donation',
        'Annadanam',
        'Construction Fund',
        'Gold/Silver Donation',
        'Corpus Fund'
      ]);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const handleDonationChange = (field, value) => {
    setDonationForm({ ...donationForm, [field]: value });
    
    // Auto-fill City and State when PIN code is entered (6 digits)
    if (field === 'pincode' && value.length === 6) {
      fetchPincodeDetails(value);
    } else if (field === 'pincode' && value.length < 6) {
      // Clear city and state if PIN code is incomplete
      setDonationForm(prev => ({ ...prev, city: '', state: '' }));
    }
  };

  const fetchPincodeDetails = async (pincode) => {
    if (!pincode || pincode.length !== 6) return;
    
    try {
      setPincodeLoading(true);
      // Using Indian Postal PIN code API
      const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
      const data = await response.json();
      
      if (data && data[0] && data[0].Status === 'Success' && data[0].PostOffice && data[0].PostOffice.length > 0) {
        const postOffice = data[0].PostOffice[0];
        setDonationForm(prev => ({
          ...prev,
          city: postOffice.District || postOffice.Name || '',
          state: postOffice.State || '',
        }));
      }
    } catch (err) {
      console.error('Error fetching PIN code details:', err);
      // Don't show error to user, just silently fail
    } finally {
      setPincodeLoading(false);
    }
  };

  const handleDonationSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const response = await api.post('/api/v1/donations/', {
        devotee_name: donationForm.devotee_name,
        devotee_phone: donationForm.devotee_phone,
        amount: parseFloat(donationForm.amount),
        category: donationForm.category,
        payment_mode: donationForm.payment_mode,
        address: donationForm.address || null,
        pincode: donationForm.pincode || null,
        city: donationForm.city || null,
        state: donationForm.state || null,
        country: donationForm.country || 'India',
      });

      setSuccess(`Donation recorded successfully! Receipt: ${response.data.receipt_number || 'N/A'}`);
      setDonationForm({
        devotee_name: '',
        devotee_phone: '',
        amount: '',
        category: '',
        payment_mode: 'Cash',
        address: '',
        pincode: '',
        city: '',
        state: '',
        country: 'India',
      });
      fetchDashboardData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Donation error:', err);
      console.error('Error details:', err.response?.data);
      
      if (err.response?.status === 404) {
        setError('API endpoint not found. Please ensure the backend server is running on http://localhost:8000 and the endpoint /api/v1/donations/ exists.');
      } else if (err.response?.status === 500) {
        const errorDetail = err.response?.data?.detail || 'Unknown server error';
        setError(`Server error: ${errorDetail}. Please check backend logs.`);
      } else if (err.response?.status === 422) {
        const errorDetail = err.response?.data?.detail || 'Validation error';
        setError(`Validation error: ${Array.isArray(errorDetail) ? errorDetail.map(e => e.msg || e).join(', ') : errorDetail}`);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.message) {
        setError(`Error: ${err.message}. Please check if backend is running.`);
      } else if (err.code === 'ECONNREFUSED' || err.code === 'ERR_NETWORK') {
        setError('Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000');
      } else {
        setError(`Error recording donation: ${JSON.stringify(err.response?.data || err.message || 'Unknown error')}. Please try again.`);
      }
    } finally {
      setSaving(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'N/A';
    const date = new Date(timeString);
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  };

  const paymentModes = ['Cash', 'Card', 'UPI', 'Cheque', 'Online'];

  const statCards = [
    { 
      title: 'Today\'s Donations', 
      value: formatCurrency(stats.todayDonations), 
      icon: <AccountBalanceIcon />, 
      color: '#4CAF50' 
    },
    { 
      title: 'Total Devotees', 
      value: stats.totalDevotees.toLocaleString(), 
      icon: <PeopleIcon />, 
      color: '#2196F3' 
    },
    { 
      title: 'Seva Bookings', 
      value: stats.sevaBookings.toString(), 
      icon: <EventIcon />, 
      color: '#FF9800' 
    },
    { 
      title: 'This Month', 
      value: formatCurrency(stats.monthDonations), 
      icon: <DashboardIcon />, 
      color: '#9C27B0' 
    },
  ];

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 4, fontWeight: 'bold' }}>
        Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {statCards.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', boxShadow: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ color: stat.color, mr: 2, fontSize: 40 }}>
                    {stat.icon}
                  </Box>
                  <Box>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Donation Entry Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              Quick Donation Entry
            </Typography>
            <Box component="form" onSubmit={handleDonationSubmit}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Devotee Name"
                    value={donationForm.devotee_name}
                    onChange={(e) => handleDonationChange('devotee_name', e.target.value)}
                    required
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    value={donationForm.devotee_phone}
                    onChange={(e) => handleDonationChange('devotee_phone', e.target.value)}
                    required
                    size="small"
                    inputProps={{ maxLength: 10 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Amount (₹)"
                    type="number"
                    value={donationForm.amount}
                    onChange={(e) => handleDonationChange('amount', e.target.value)}
                    required
                    size="small"
                    inputProps={{ min: 1, step: 0.01 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Street Address (Optional)"
                    placeholder="House/Flat No., Building, Street, Area"
                    value={donationForm.address}
                    onChange={(e) => handleDonationChange('address', e.target.value)}
                    size="small"
                    multiline
                    rows={2}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="PIN Code"
                    placeholder="6 digit PIN code"
                    value={donationForm.pincode}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                      handleDonationChange('pincode', value);
                    }}
                    size="small"
                    inputProps={{ maxLength: 6 }}
                    InputProps={{
                      endAdornment: pincodeLoading && (
                        <InputAdornment position="end">
                          <CircularProgress size={20} />
                        </InputAdornment>
                      )
                    }}
                    helperText={donationForm.pincode.length === 6 ? "City & State will auto-fill" : ""}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="City"
                    placeholder="City"
                    value={donationForm.city}
                    onChange={(e) => handleDonationChange('city', e.target.value)}
                    size="small"
                    disabled={pincodeLoading}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="State"
                    placeholder="State"
                    value={donationForm.state}
                    onChange={(e) => handleDonationChange('state', e.target.value)}
                    size="small"
                    disabled={pincodeLoading}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Country"
                    placeholder="Country"
                    value={donationForm.country}
                    onChange={(e) => handleDonationChange('country', e.target.value)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Category"
                    value={donationForm.category}
                    onChange={(e) => handleDonationChange('category', e.target.value)}
                    required
                    size="small"
                  >
                    {categories.map((cat) => (
                      <MenuItem key={cat} value={cat}>
                        {cat}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Payment Mode"
                    value={donationForm.payment_mode}
                    onChange={(e) => handleDonationChange('payment_mode', e.target.value)}
                    required
                    size="small"
                  >
                    {paymentModes.map((mode) => (
                      <MenuItem key={mode} value={mode}>
                        {mode}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                    disabled={saving}
                    size="large"
                  >
                    {saving ? 'Saving...' : 'Record Donation'}
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        </Grid>

        {/* Panchang Display */}
        <Grid item xs={12} md={6}>
          <PanchangDisplay 
            data={panchangData} 
            settings={panchangData}
            compact={true}
          />
          <Button
            variant="outlined"
            fullWidth
            size="small"
            sx={{ mt: 2 }}
            onClick={() => navigate('/panchang')}
          >
            View Full Panchang →
          </Button>
        </Grid>
      </Grid>
    </Layout>
  );
}

export default Dashboard;
