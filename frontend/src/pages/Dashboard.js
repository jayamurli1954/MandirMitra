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
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Collapse,
} from '@mui/material';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import EventIcon from '@mui/icons-material/Event';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../components/Layout';
import PanchangRibbon from '../components/PanchangRibbon';
import api from '../services/api';

function Dashboard() {
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
    name_prefix: '',
    devotee_first_name: '',
    devotee_last_name: '',
    devotee_phone: '',
    country_code: '+91',
    amount: '',
    category: '',
    donation_type: 'cash',
    payment_mode: 'Cash',
    bank_account_id: '',
    // UPI Payment Details
    sender_upi_id: '',
    upi_reference_number: '',
    // Cheque Payment Details
    cheque_number: '',
    cheque_date: '',
    cheque_bank_name: '',
    cheque_branch: '',
    // Online Transfer Details
    utr_number: '',
    payer_name: '',
    is_anonymous: false,
    address: '',  // Street address
    pincode: '',
    city: '',
    state: '',
    country: 'India',
  });
  const [pincodeLoading, setPincodeLoading] = useState(false);
  const [searchingDevotee, setSearchingDevotee] = useState(false);
  const [categories, setCategories] = useState([]);
  const [bankAccounts, setBankAccounts] = useState([]);
  const [saving, setSaving] = useState(false);
  const [mobileEntered, setMobileEntered] = useState(false); // Track if mobile number is entered

  useEffect(() => {
    fetchDashboardData();
    fetchCategories();
    fetchBankAccounts();
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

  const fetchBankAccounts = async () => {
    try {
      const response = await api.get('/api/v1/donations/bank-accounts');
      if (response.data) {
        setBankAccounts(response.data);
      }
    } catch (err) {
      console.error('Error fetching bank accounts:', err);
      // Don't show error, just silently fail
    }
  };

  const handleDonationChange = async (field, value) => {
    const updatedForm = { ...donationForm, [field]: value };
    setDonationForm(updatedForm);
    
    // Mobile-first: Enable other fields only after mobile is entered (10 digits for India)
    if (field === 'devotee_phone') {
      const phoneLength = value.length;
      const countryCode = updatedForm.country_code || '+91';
      
      // For India (+91), require 10 digits; for others, require at least 7 digits
      const isValidLength = (countryCode === '+91' && phoneLength === 10) || 
                           (countryCode !== '+91' && phoneLength >= 7);
      
      setMobileEntered(isValidLength);
      
      // Auto-fill devotee details when mobile is entered
      if (isValidLength) {
        setSearchingDevotee(true);
        try {
          // Search with the selected country code
          const searchPhone = `${countryCode}${value}`;
          const response = await api.get(`/api/v1/devotees/search/by-mobile/${searchPhone}`);
        if (response.data && response.data.length > 0) {
          // If multiple results, use the first one (prioritized by country code match)
          const devotee = response.data[0];
          // If multiple results with different country codes, log it
          if (response.data.length > 1) {
            console.log(`Multiple devotees found for phone ${value}. Using first match.`);
          }
          setDonationForm(prev => ({
            ...prev,
            name_prefix: devotee.name_prefix || prev.name_prefix,
            devotee_first_name: devotee.first_name || (devotee.name ? devotee.name.split(' ')[0] : '') || prev.devotee_first_name,
            devotee_last_name: devotee.last_name || (devotee.name && devotee.name.split(' ').length > 1 ? devotee.name.split(' ').slice(1).join(' ') : '') || prev.devotee_last_name,
            country_code: devotee.country_code || prev.country_code || '+91',
            address: devotee.address || prev.address,
            pincode: devotee.pincode || prev.pincode,
            city: devotee.city || prev.city,
            state: devotee.state || prev.state,
            country: devotee.country || prev.country || 'India',
          }));
        }
      } catch (err) {
        // Devotee not found is ok; user will enter details manually
        console.log('Devotee not found for mobile:', value);
      } finally {
        setSearchingDevotee(false);
      }
      } else {
        // If mobile is cleared or incomplete, disable other fields
        setMobileEntered(false);
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
      // Dashboard only supports Cash donations
      const payload = {
        devotee_first_name: donationForm.devotee_first_name || '',
        devotee_last_name: donationForm.devotee_last_name || undefined,
        devotee_name: `${donationForm.devotee_first_name} ${donationForm.devotee_last_name || ''}`.trim(), // For backward compatibility
        devotee_phone: donationForm.devotee_phone,
        name_prefix: donationForm.name_prefix || undefined,
        country_code: donationForm.country_code || '+91',
        amount: parseFloat(donationForm.amount),
        category: donationForm.category,
        donation_type: 'cash',  // Dashboard only supports cash donations
        payment_mode: donationForm.payment_mode,
        is_anonymous: donationForm.is_anonymous || false,
        // Payment-specific fields
        sender_upi_id: donationForm.sender_upi_id || undefined,
        upi_reference_number: donationForm.upi_reference_number || undefined,
        cheque_number: donationForm.cheque_number || undefined,
        cheque_date: donationForm.cheque_date || undefined,
        cheque_bank_name: donationForm.cheque_bank_name || undefined,
        cheque_branch: donationForm.cheque_branch || undefined,
        utr_number: donationForm.utr_number || undefined,
        payer_name: donationForm.payer_name || undefined,
        address: donationForm.address || null,
        pincode: donationForm.pincode || null,
        city: donationForm.city || null,
        state: donationForm.state || null,
        country: donationForm.country || 'India',
      };
      
      // Add bank_account_id for non-cash payments
      if (donationForm.payment_mode !== 'Cash' && donationForm.bank_account_id) {
        payload.bank_account_id = parseInt(donationForm.bank_account_id);
      }
      
      const response = await api.post('/api/v1/donations/', payload);

      setSuccess(`Donation recorded successfully! Receipt: ${response.data.receipt_number || 'N/A'}`);
      setDonationForm({
        name_prefix: '',
        devotee_first_name: '',
        devotee_last_name: '',
        devotee_phone: '',
        country_code: '+91',
        amount: '',
        category: '',
        donation_type: 'cash',
        payment_mode: 'Cash',
        bank_account_id: '',
        sender_upi_id: '',
        upi_reference_number: '',
        cheque_number: '',
        cheque_date: '',
        cheque_bank_name: '',
        cheque_branch: '',
        utr_number: '',
        payer_name: '',
        is_anonymous: false,
        address: '',
        pincode: '',
        city: '',
        state: '',
        country: 'India',
      });
      setMobileEntered(false); // Reset mobile entered state
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

      {/* Panchang Ribbon at Top */}
      <PanchangRibbon data={panchangData} settings={panchangData} />

      {/* Compact Stats Row: Donations & Sevas - Single Row */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={1.5}>
          {/* Donations - More Compact */}
          {donationCards.map((stat, index) => (
            <Grid item xs={6} sm={2} key={index}>
              <Card sx={{ boxShadow: 1, borderLeft: `3px solid ${stat.color}`, height: '100%' }}>
                <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', mb: 0.3, fontSize: '1rem' }}>
                        {stat.value}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem', display: 'block' }}>
                        {stat.title}
                      </Typography>
                      {stat.subtitle && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.3, fontSize: '0.65rem' }}>
                          {stat.subtitle}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ color: stat.color, fontSize: 24, ml: 1 }}>
                      {stat.icon}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {/* Sevas - More Compact */}
          {sevaCards.map((stat, index) => (
            <Grid item xs={6} sm={2} key={index}>
              <Card sx={{ boxShadow: 1, borderLeft: `3px solid ${stat.color}`, height: '100%' }}>
                <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="h6" component="div" sx={{ fontWeight: 'bold', mb: 0.3, fontSize: '1rem' }}>
                        {stat.value}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem', display: 'block' }}>
                        {stat.title}
                      </Typography>
                      {stat.subtitle && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.3, fontSize: '0.65rem' }}>
                          {stat.subtitle}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ color: stat.color, fontSize: 24, ml: 1 }}>
                      {stat.icon}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Quick Donation Entry - Full Width */}
      <Paper sx={{ p: 3, boxShadow: 2, mt: 2 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          Quick Donation Entry
        </Typography>
        <Box component="form" onSubmit={handleDonationSubmit}>
          <Grid container spacing={2}>
            {/* Mobile Number - Must be entered first */}
            <Grid item xs={12} sm={2}>
              <TextField
                fullWidth
                select
                label="Country Code"
                value={donationForm.country_code || '+91'}
                onChange={(e) => handleDonationChange('country_code', e.target.value)}
                size="small"
                disabled={mobileEntered}
              >
                <MenuItem value="+91">+91</MenuItem>
                <MenuItem value="+1">+1</MenuItem>
                <MenuItem value="+44">+44</MenuItem>
                <MenuItem value="+971">+971</MenuItem>
                <MenuItem value="+65">+65</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Mobile Number *"
                value={donationForm.devotee_phone}
                onChange={(e) => handleDonationChange('devotee_phone', e.target.value)}
                required
                size="small"
                inputProps={{ maxLength: 15 }}
                helperText={
                  mobileEntered
                    ? (donationForm.devotee_first_name ? '✓ Devotee found' : 'New devotee - enter details')
                    : 'Enter mobile number first to continue'
                }
                InputProps={{
                  endAdornment: searchingDevotee && (
                    <InputAdornment position="end">
                      <CircularProgress size={18} />
                    </InputAdornment>
                  )
                }}
                sx={{
                  '& .MuiInputBase-root': {
                    bgcolor: mobileEntered ? 'transparent' : '#f5f5f5',
                  }
                }}
              />
            </Grid>
            
            {/* Divider and Info */}
            {!mobileEntered && (
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mt: 1 }}>
                  Please enter mobile number first to enable other fields
                </Alert>
              </Grid>
            )}

            {/* Devotee Details - Only enabled after mobile is entered */}
            {mobileEntered && (
              <>
                {/* Name Prefix */}
                <Grid item xs={12} sm={2}>
                  <TextField
                    fullWidth
                    select
                    label="Prefix"
                    value={donationForm.name_prefix || ''}
                    onChange={(e) => handleDonationChange('name_prefix', e.target.value)}
                    size="small"
                  >
                    <MenuItem value="">None</MenuItem>
                    <MenuItem value="Mr.">Mr.</MenuItem>
                    <MenuItem value="Mrs.">Mrs.</MenuItem>
                    <MenuItem value="Ms.">Ms.</MenuItem>
                    <MenuItem value="M/s">M/s</MenuItem>
                    <MenuItem value="Dr.">Dr.</MenuItem>
                    <MenuItem value="Shri">Shri</MenuItem>
                    <MenuItem value="Smt.">Smt.</MenuItem>
                    <MenuItem value="Kum.">Kum.</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={2.5}>
                  <TextField
                    fullWidth
                    label="First Name *"
                    value={donationForm.devotee_first_name}
                    onChange={(e) => handleDonationChange('devotee_first_name', e.target.value)}
                    required
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={donationForm.devotee_last_name}
                    onChange={(e) => handleDonationChange('devotee_last_name', e.target.value)}
                    size="small"
                  />
                </Grid>
                
                {/* Amount and Category */}
                <Grid item xs={12} sm={4}>
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
                <Grid item xs={12} sm={4}>
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
                {/* Payment Mode */}
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Payment Mode *"
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
                {/* Bank Account - for non-cash payments */}
                {donationForm.payment_mode !== 'Cash' && (
                  <Grid item xs={12} sm={6}>
                    {bankAccounts.length > 0 ? (
                      <TextField
                        fullWidth
                        select
                        label="Bank Account *"
                        value={donationForm.bank_account_id || ''}
                        onChange={(e) => handleDonationChange('bank_account_id', e.target.value)}
                        required
                        size="small"
                        helperText={`Select which bank account received this ${donationForm.payment_mode} payment`}
                      >
                        {bankAccounts.map((account) => {
                          const accountName = account.name || account.account_name || 'Account';
                          const bankName = account.bank_name || 'Bank';
                          const accountNumber = account.account_number ? ` (****${account.account_number.slice(-4)})` : '';
                          return (
                            <MenuItem key={account.id} value={account.id}>
                              {accountName} - {bankName}{accountNumber} {account.is_primary ? '(Primary)' : ''}
                            </MenuItem>
                          );
                        })}
                      </TextField>
                    ) : (
                      <Alert severity="warning" sx={{ mt: 1 }}>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          No bank accounts configured. To record {donationForm.payment_mode} payments, please add bank accounts.
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Go to: Accounting → UPI Payments → Bank Accounts (or Settings → Banking)
                        </Typography>
                      </Alert>
                    )}
                  </Grid>
                )}
                
                {/* Payment-specific fields based on payment_mode */}
                {donationForm.payment_mode === 'UPI' && (
                  <>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Sender UPI ID"
                        value={donationForm.sender_upi_id || ''}
                        onChange={(e) => handleDonationChange('sender_upi_id', e.target.value)}
                        size="small"
                        placeholder="9876543210@paytm"
                        helperText="From SMS notification (e.g., VPA)"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="UPI Reference Number"
                        value={donationForm.upi_reference_number || ''}
                        onChange={(e) => handleDonationChange('upi_reference_number', e.target.value)}
                        size="small"
                        placeholder="UTR/RRN from SMS"
                        helperText="Transaction reference from SMS"
                      />
                    </Grid>
                  </>
                )}
                
                {donationForm.payment_mode === 'Cheque' && (
                  <>
                    <Grid item xs={12} sm={3}>
                      <TextField
                        fullWidth
                        label="Cheque Number *"
                        value={donationForm.cheque_number || ''}
                        onChange={(e) => handleDonationChange('cheque_number', e.target.value)}
                        required
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <TextField
                        fullWidth
                        label="Cheque Date *"
                        type="date"
                        value={donationForm.cheque_date || ''}
                        onChange={(e) => handleDonationChange('cheque_date', e.target.value)}
                        required
                        size="small"
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <TextField
                        fullWidth
                        label="Bank Name *"
                        value={donationForm.cheque_bank_name || ''}
                        onChange={(e) => handleDonationChange('cheque_bank_name', e.target.value)}
                        required
                        size="small"
                        placeholder="e.g., SBI, HDFC"
                      />
                    </Grid>
                    <Grid item xs={12} sm={3}>
                      <TextField
                        fullWidth
                        label="Branch"
                        value={donationForm.cheque_branch || ''}
                        onChange={(e) => handleDonationChange('cheque_branch', e.target.value)}
                        size="small"
                        placeholder="Branch name"
                      />
                    </Grid>
                  </>
                )}
                
                {donationForm.payment_mode === 'Online' && (
                  <>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="UTR Number *"
                        value={donationForm.utr_number || ''}
                        onChange={(e) => handleDonationChange('utr_number', e.target.value)}
                        required
                        size="small"
                        placeholder="Unique Transfer Reference"
                        helperText="UTR or transaction reference from bank"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Payer Name"
                        value={donationForm.payer_name || ''}
                        onChange={(e) => handleDonationChange('payer_name', e.target.value)}
                        size="small"
                        placeholder="Name of person who made the transfer"
                        helperText="May be different from devotee name"
                      />
                    </Grid>
                  </>
                )}
                
                {/* Anonymous Checkbox */}
                <Grid item xs={12} sm={4}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={donationForm.is_anonymous || false}
                        onChange={(e) => handleDonationChange('is_anonymous', e.target.checked)}
                        size="small"
                      />
                    }
                    label="Anonymous Donation"
                  />
                </Grid>
                
                {/* Address Fields - Collapsible */}
                <Grid item xs={12}>
                  <Collapse in={!donationForm.is_anonymous}>
                    <Grid container spacing={2}>
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
                    </Grid>
                  </Collapse>
                </Grid>
                
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                    disabled={saving || !mobileEntered}
                    size="large"
                    sx={{ mt: 2 }}
                  >
                    {saving ? 'Saving...' : 'Record Donation'}
                  </Button>
                </Grid>
              </>
            )}
          </Grid>
        </Box>
      </Paper>
    </Layout>
  );
}

export default Dashboard;
