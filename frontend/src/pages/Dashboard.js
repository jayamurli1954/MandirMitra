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
    donations: {
      today: { amount: 0, count: 0 },
      month: { amount: 0, count: 0 },
      year: { amount: 0, count: 0 }
    },
    sevas: {
      today: { amount: 0, count: 0 },
      month: { amount: 0, count: 0 },
      year: { amount: 0, count: 0 }
    }
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
  const [searchingDevotee, setSearchingDevotee] = useState(false);
  const [categories, setCategories] = useState([]);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchCategories();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, panchangSettingsRes, panchangDataRes] = await Promise.allSettled([
        api.get('/api/v1/dashboard/stats'),
        api.get('/api/v1/panchang/display-settings/'),
        api.get('/api/v1/panchang/today'),
      ]);

      // Get dashboard stats
      if (statsRes.status === 'fulfilled' && statsRes.value.data) {
        setStats(statsRes.value.data);
      } else {
        // Fallback to empty stats
        setStats({
          donations: { today: { amount: 0, count: 0 }, month: { amount: 0, count: 0 }, year: { amount: 0, count: 0 } },
          sevas: { today: { amount: 0, count: 0 }, month: { amount: 0, count: 0 }, year: { amount: 0, count: 0 } }
        });
      }

      // Fetch panchang settings and data
      let panchangSettings = null;
      let panchangData = null;
      
      if (panchangSettingsRes.status === 'fulfilled' && panchangSettingsRes.value.data) {
        panchangSettings = panchangSettingsRes.value.data;
      }
      
      if (panchangDataRes.status === 'fulfilled' && panchangDataRes.value.data) {
        panchangData = panchangDataRes.value.data;
      } else if (panchangDataRes.status === 'rejected') {
        const error = panchangDataRes.reason;
        if (error?.code === 'ERR_NETWORK' || error?.message?.includes('Network Error')) {
          console.warn('Panchang API: Backend server not reachable. Ensure backend is running on http://localhost:8000');
        } else {
          console.log('Panchang data API failed:', error);
        }
      }
      
      // Set panchang data (merge settings if available)
      if (panchangData) {
        setPanchangData({
          ...panchangData,
          ...(panchangSettings || {})
        });
      } else if (panchangSettings) {
        setPanchangData(panchangSettings);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setStats({
        donations: { today: { amount: 0, count: 0 }, month: { amount: 0, count: 0 }, year: { amount: 0, count: 0 } },
        sevas: { today: { amount: 0, count: 0 }, month: { amount: 0, count: 0 }, year: { amount: 0, count: 0 } }
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

  const handleDonationChange = async (field, value) => {
    const updatedForm = { ...donationForm, [field]: value };
    setDonationForm(updatedForm);
    
    // Mobile-first: when 10-digit mobile is entered, auto-fill devotee details if found
    if (field === 'devotee_phone' && value && value.length === 10) {
      setSearchingDevotee(true);
      try {
        const response = await api.get(`/api/v1/devotees/search/by-mobile/${value}`);
        if (response.data) {
          setDonationForm(prev => ({
            ...prev,
            devotee_name: response.data.name || prev.devotee_name,
            address: response.data.address || prev.address,
            pincode: response.data.pincode || prev.pincode,
            city: response.data.city || prev.city,
            state: response.data.state || prev.state,
            country: response.data.country || prev.country || 'India',
          }));
        }
      } catch (err) {
        // Devotee not found is ok; user will enter details manually
        console.log('Devotee not found for mobile:', value);
      } finally {
        setSearchingDevotee(false);
      }
    }
    
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

  // First row: Donations
  const donationCards = [
    { 
      title: 'Today\'s Donation', 
      value: formatCurrency(stats.donations.today.amount),
      subtitle: `${stats.donations.today.count} donations`,
      icon: <AccountBalanceIcon />, 
      color: '#4CAF50' 
    },
    { 
      title: 'Cumulative for Month', 
      value: formatCurrency(stats.donations.month.amount),
      subtitle: `${stats.donations.month.count} donations`,
      icon: <AccountBalanceIcon />, 
      color: '#2196F3' 
    },
    { 
      title: 'Cumulative for Year', 
      value: formatCurrency(stats.donations.year.amount),
      subtitle: `${stats.donations.year.count} donations`,
      icon: <AccountBalanceIcon />, 
      color: '#9C27B0' 
    },
  ];

  // Second row: Sevas
  const sevaCards = [
    { 
      title: 'Today\'s Seva', 
      value: formatCurrency(stats.sevas.today.amount),
      subtitle: `${stats.sevas.today.count} bookings`,
      icon: <EventIcon />, 
      color: '#FF9800' 
    },
    { 
      title: 'Cumulative for Month', 
      value: formatCurrency(stats.sevas.month.amount),
      subtitle: `${stats.sevas.month.count} bookings`,
      icon: <EventIcon />, 
      color: '#FF6B35' 
    },
    { 
      title: 'Cumulative for Year', 
      value: formatCurrency(stats.sevas.year.amount),
      subtitle: `${stats.sevas.year.count} bookings`,
      icon: <EventIcon />, 
      color: '#E91E63' 
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

      {/* Compact Stats Row: Donations & Sevas */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          {/* Donations - Compact */}
          <Grid item xs={12}>
            <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 600, color: '#4CAF50' }}>
              💰 Donations
            </Typography>
            <Grid container spacing={2}>
              {donationCards.map((stat, index) => (
                <Grid item xs={12} sm={4} key={index}>
                  <Card sx={{ boxShadow: 1, borderLeft: `4px solid ${stat.color}` }}>
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                            {stat.value}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
                            {stat.title}
                          </Typography>
                          {stat.subtitle && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                              {stat.subtitle}
                            </Typography>
                          )}
                        </Box>
                        <Box sx={{ color: stat.color, fontSize: 32 }}>
                          {stat.icon}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>

          {/* Sevas - Compact */}
          <Grid item xs={12} sx={{ mt: 2 }}>
            <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 600, color: '#FF9800' }}>
              🕉️ Sevas
            </Typography>
            <Grid container spacing={2}>
              {sevaCards.map((stat, index) => (
                <Grid item xs={12} sm={4} key={index}>
                  <Card sx={{ boxShadow: 1, borderLeft: `4px solid ${stat.color}` }}>
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                            {stat.value}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
                            {stat.title}
                          </Typography>
                          {stat.subtitle && (
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                              {stat.subtitle}
                            </Typography>
                          )}
                        </Box>
                        <Box sx={{ color: stat.color, fontSize: 32 }}>
                          {stat.icon}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>
      </Box>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Donation Entry Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, boxShadow: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
              Quick Donation Entry
            </Typography>
            <Box component="form" onSubmit={handleDonationSubmit}>
              <Grid container spacing={2}>
                {/* Mobile Number - FIRST FIELD */}
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Mobile Number *"
                    value={donationForm.devotee_phone}
                    onChange={(e) => handleDonationChange('devotee_phone', e.target.value)}
                    required
                    size="small"
                    inputProps={{ maxLength: 10 }}
                    helperText={
                      donationForm.devotee_phone.length === 10
                        ? (donationForm.devotee_name ? '✓ Existing devotee auto-filled' : 'New devotee – enter details')
                        : 'Enter 10-digit mobile'
                    }
                    InputProps={{
                      endAdornment: searchingDevotee && (
                        <InputAdornment position="end">
                          <CircularProgress size={18} />
                        </InputAdornment>
                      )
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Devotee Name *"
                    value={donationForm.devotee_name}
                    onChange={(e) => handleDonationChange('devotee_name', e.target.value)}
                    required
                    size="small"
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

        {/* Panchang Display - Side by side with donation form */}
        <Grid item xs={12} md={6}>
          {panchangData ? (
            <>
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
            </>
          ) : (
            <Paper sx={{ p: 3, boxShadow: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Panchang data will be displayed here once connected to panchang service API.
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Layout>
  );
}

export default Dashboard;
