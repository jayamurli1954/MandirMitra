import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Checkbox,
  FormControlLabel,
  Collapse,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import DownloadIcon from '@mui/icons-material/Download';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

function Donations() {
  const { showSuccess, showError } = useNotification();
  const [donations, setDonations] = useState([
    { 
      name_prefix: '',
      devotee_first_name: '', 
      devotee_last_name: '',
      devotee_phone: '', 
      country_code: '+91',
      pincode: '', 
      city: '', 
      state: '', 
      country: 'India', 
      amount: '', 
      category: '', 
      payment_mode: 'Cash',
      donation_type: 'cash',
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
      // In-kind fields
      inkind_subtype: '',
      item_name: '',
      item_description: '',
      quantity: '',
      unit: '',
      value_assessed: ''
    }
  ]);
  const [categories, setCategories] = useState([]);
  const [devotees, setDevotees] = useState([]);
  const [bankAccounts, setBankAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [donationList, setDonationList] = useState([]);
  const [searchingDevotees, setSearchingDevotees] = useState({});
  const [tabValue, setTabValue] = useState(0);
  const [bulkImportDialogOpen, setBulkImportDialogOpen] = useState(false);
  const [bulkImportFile, setBulkImportFile] = useState(null);
  const [bulkImportLoading, setBulkImportLoading] = useState(false);
  const [bulkImportResult, setBulkImportResult] = useState(null);

  const paymentModes = ['Cash', 'Card', 'UPI', 'Cheque', 'Online'];

  useEffect(() => {
    fetchCategories();
    fetchDevotees();
    fetchDonations();
    fetchBankAccounts();
  }, []);

  const fetchBankAccounts = async () => {
    try {
      const response = await api.get('/api/v1/donations/bank-accounts');
      if (response.data) {
        setBankAccounts(response.data);
      }
    } catch (err) {
      console.error('Error fetching bank accounts:', err);
    }
  };

  const fetchCategories = async () => {
    try {
      // TODO: Replace with actual API endpoint
      // For now, use default categories
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

  const fetchDevotees = async () => {
    try {
      const response = await api.get('/api/v1/devotees');
      if (response.data) {
        setDevotees(response.data);
      }
    } catch (err) {
      console.error('Error fetching devotees:', err);
    }
  };

  const fetchDonations = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/donations');
      if (response.data) {
        setDonationList(response.data);
      }
    } catch (err) {
      console.error('Error fetching donations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRow = () => {
    if (donations.length < 5) {
      setDonations([...donations, { 
        name_prefix: '',
        devotee_first_name: '',
        devotee_last_name: '',
        devotee_phone: '', 
        country_code: '+91',
        pincode: '', 
        city: '', 
        state: '', 
        country: 'India', 
        amount: '', 
        category: '', 
        payment_mode: 'Cash',
        donation_type: 'cash',
        bank_account_id: '',
        is_anonymous: false,
        inkind_subtype: '',
        item_name: '',
        item_description: '',
        quantity: '',
        unit: '',
        value_assessed: ''
      }]);
    }
  };

  const handleRemoveRow = (index) => {
    if (donations.length > 1) {
      setDonations(donations.filter((_, i) => i !== index));
    }
  };

  const lookupPincode = async (pincode) => {
    if (!pincode || pincode.length !== 6) return null;
    
    try {
      const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
      const data = await response.json();
      
      if (data && data[0] && data[0].Status === 'Success' && data[0].PostOffice && data[0].PostOffice.length > 0) {
        const postOffice = data[0].PostOffice[0];
        return {
          city: postOffice.District || postOffice.Name || '',
          state: postOffice.State || '',
          country: 'India'
        };
      }
    } catch (err) {
      console.error('Error looking up pincode:', err);
    }
    return null;
  };

  const handleChange = async (index, field, value) => {
    const updated = [...donations];
    updated[index][field] = value;
    
    // Auto-fill devotee details when mobile number is entered
    // Search when phone number is entered (handle different lengths for different countries)
    if (field === 'devotee_phone' && value) {
      // For India (+91), search when 10 digits are entered
      // For other countries, search when reasonable length is reached
      const countryCode = updated[index].country_code || '+91';
      const shouldSearch = (countryCode === '+91' && value.length === 10) || 
                          (countryCode !== '+91' && value.length >= 7);
      
      if (shouldSearch) {
        setSearchingDevotees({ ...searchingDevotees, [index]: true });
        try {
          // Search with country code + phone number
          const fullPhone = `${countryCode}${value}`;
          // Always search with +91 first (default to India)
          const searchPhone = countryCode === '+91' ? `+91${value}` : fullPhone;
          const response = await api.get(`/api/v1/devotees/search/by-mobile/${searchPhone}`);
          if (response.data && response.data.length > 0) {
            // If multiple results, use the first one (prioritized by country code match)
            const devotee = response.data[0];
            // If multiple results with different country codes, show selection dialog
            if (response.data.length > 1) {
              // For now, use the first match (exact country code match is first)
              // TODO: Could show a dialog to select from multiple matches
              console.log(`Multiple devotees found for phone ${value}. Using first match.`);
            }
            // Devotee found - auto-fill all details
            updated[index].name_prefix = devotee.name_prefix || '';
            updated[index].devotee_first_name = devotee.first_name || (devotee.name ? devotee.name.split(' ')[0] : '');
            updated[index].devotee_last_name = devotee.last_name || (devotee.name && devotee.name.split(' ').length > 1 ? devotee.name.split(' ').slice(1).join(' ') : '');
            updated[index].country_code = devotee.country_code || countryCode;
            updated[index].pincode = devotee.pincode || '';
            updated[index].city = devotee.city || '';
            updated[index].state = devotee.state || '';
            updated[index].country = devotee.country || 'India';
          }
        } catch (err) {
          // Devotee not found - that's okay, user will enter manually
          console.log('Devotee not found for mobile:', value);
        } finally {
          setSearchingDevotees({ ...searchingDevotees, [index]: false });
        }
      }
    }
    
    // Auto-fill city/state/country when PIN code is entered
    if (field === 'pincode' && value && value.length === 6) {
      const locationData = await lookupPincode(value);
      if (locationData) {
        updated[index].city = locationData.city || '';
        updated[index].state = locationData.state || '';
        updated[index].country = locationData.country || 'India';
      }
    }
    
    setDonations(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      // Validate all entries
      const validDonations = donations.filter(d => 
        (d.devotee_first_name || d.devotee_name) && d.devotee_phone && d.amount && d.category
      );

      if (validDonations.length === 0) {
        setError('Please fill at least one donation entry');
        setSaving(false);
        return;
      }

      // Save each donation
      const promises = validDonations.map(donation => {
        const payload = {
          devotee_name: donation.devotee_name,
          devotee_phone: donation.devotee_phone,
          name_prefix: donation.name_prefix || undefined,
          country_code: donation.country_code || '+91',
          amount: parseFloat(donation.amount),
          category: donation.category,
          donation_type: donation.donation_type || 'cash',
          is_anonymous: donation.is_anonymous || false,
          pincode: donation.pincode || undefined,
          city: donation.city || undefined,
          state: donation.state || undefined,
          country: donation.country || 'India',
        };
        
        // Add payment_mode and bank_account_id only for cash donations
        if (donation.donation_type === 'cash') {
          payload.payment_mode = donation.payment_mode;
          // Add bank_account_id for non-cash payments
          if (donation.payment_mode !== 'Cash' && donation.bank_account_id) {
            payload.bank_account_id = parseInt(donation.bank_account_id);
          }
          // Add payment-specific fields
          if (donation.payment_mode === 'UPI') {
            payload.sender_upi_id = donation.sender_upi_id || undefined;
            payload.upi_reference_number = donation.upi_reference_number || undefined;
          } else if (donation.payment_mode === 'Cheque') {
            payload.cheque_number = donation.cheque_number || undefined;
            payload.cheque_date = donation.cheque_date || undefined;
            payload.cheque_bank_name = donation.cheque_bank_name || undefined;
            payload.cheque_branch = donation.cheque_branch || undefined;
          } else if (donation.payment_mode === 'Online') {
            payload.utr_number = donation.utr_number || undefined;
            payload.payer_name = donation.payer_name || undefined;
          }
        }
        
        // Add in-kind fields if donation type is in_kind
        if (donation.donation_type === 'in_kind') {
          payload.inkind_subtype = donation.inkind_subtype || undefined;
          payload.item_name = donation.item_name || undefined;
          payload.item_description = donation.item_description || undefined;
          payload.quantity = donation.quantity ? parseFloat(donation.quantity) : undefined;
          payload.unit = donation.unit || undefined;
          payload.value_assessed = donation.value_assessed ? parseFloat(donation.value_assessed) : parseFloat(donation.amount);
        }
        
        return api.post('/api/v1/donations', payload);
      });

      await Promise.all(promises);
      
      setSuccess(`Successfully recorded ${validDonations.length} donation(s)!`);
      setDonations([{ 
        name_prefix: '',
        devotee_name: '', 
        devotee_phone: '', 
        country_code: '+91',
        pincode: '', 
        city: '', 
        state: '', 
        country: 'India', 
        amount: '', 
        category: '', 
        payment_mode: 'Cash',
        donation_type: 'cash',
        bank_account_id: '',
        is_anonymous: false,
        inkind_subtype: '',
        item_name: '',
        item_description: '',
        quantity: '',
        unit: '',
        value_assessed: ''
      }]);
      fetchDonations();
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error recording donations');
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

  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
        Donations
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Paper sx={{ mt: 2 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Record Donations" />
          <Tab label="Donation List" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Record Donations (Up to 5 entries)
          </Typography>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={handleAddRow}
            disabled={donations.length >= 5}
          >
            Add Entry
          </Button>
        </Box>

        <Box component="form" onSubmit={handleSubmit}>
          {donations.map((donation, index) => (
            <Paper key={index} sx={{ p: 2, mb: 2, bgcolor: '#f9f9f9' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  Entry {index + 1}
                </Typography>
                {donations.length > 1 && (
                  <IconButton
                    color="error"
                    onClick={() => handleRemoveRow(index)}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>

              <Grid container spacing={2}>
                {/* Name Prefix */}
                <Grid item xs={12} sm={6} md={1.5}>
                  <TextField
                    fullWidth
                    select
                    label="Prefix"
                    value={donation.name_prefix || ''}
                    onChange={(e) => handleChange(index, 'name_prefix', e.target.value)}
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
                {/* First Name - Auto-filled when mobile found */}
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="First Name *"
                    value={donation.devotee_first_name}
                    onChange={(e) => handleChange(index, 'devotee_first_name', e.target.value)}
                    required
                    size="small"
                    helperText={donation.devotee_first_name ? '✓ Auto-filled' : ''}
                  />
                </Grid>
                {/* Last Name - Auto-filled when mobile found */}
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={donation.devotee_last_name}
                    onChange={(e) => handleChange(index, 'devotee_last_name', e.target.value)}
                    size="small"
                    helperText={donation.devotee_last_name ? '✓ Auto-filled' : ''}
                  />
                </Grid>
                {/* Country Code */}
                <Grid item xs={12} sm={6} md={1.5}>
                  <TextField
                    fullWidth
                    select
                    label="Country Code"
                    value={donation.country_code || '+91'}
                    onChange={(e) => handleChange(index, 'country_code', e.target.value)}
                    size="small"
                  >
                    <MenuItem value="+91">+91 (India)</MenuItem>
                    <MenuItem value="+1">+1 (USA/Canada)</MenuItem>
                    <MenuItem value="+44">+44 (UK)</MenuItem>
                    <MenuItem value="+971">+971 (UAE)</MenuItem>
                    <MenuItem value="+65">+65 (Singapore)</MenuItem>
                    <MenuItem value="+61">+61 (Australia)</MenuItem>
                    <MenuItem value="+27">+27 (South Africa)</MenuItem>
                    <MenuItem value="+60">+60 (Malaysia)</MenuItem>
                    <MenuItem value="+66">+66 (Thailand)</MenuItem>
                    <MenuItem value="+94">+94 (Sri Lanka)</MenuItem>
                    <MenuItem value="+880">+880 (Bangladesh)</MenuItem>
                    <MenuItem value="+977">+977 (Nepal)</MenuItem>
                    <MenuItem value="+92">+92 (Pakistan)</MenuItem>
                  </TextField>
                </Grid>
                {/* Mobile Number */}
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="Mobile Number *"
                    value={donation.devotee_phone}
                    onChange={(e) => handleChange(index, 'devotee_phone', e.target.value)}
                    required
                    size="small"
                    inputProps={{ maxLength: 15 }}
                    helperText={searchingDevotees[index] ? 'Searching...' : 'Enter mobile number'}
                    InputProps={{
                      endAdornment: searchingDevotees[index] ? <CircularProgress size={16} /> : null
                    }}
                  />
                </Grid>
                {/* PIN Code - Early field for auto-fill */}
                <Grid item xs={12} sm={6} md={1.5}>
                  <TextField
                    fullWidth
                    label="PIN Code"
                    value={donation.pincode}
                    onChange={(e) => handleChange(index, 'pincode', e.target.value)}
                    size="small"
                    inputProps={{ maxLength: 6 }}
                    helperText="Auto-fills city/state"
                  />
                </Grid>
                {/* City - Auto-filled from PIN */}
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="City"
                    value={donation.city}
                    onChange={(e) => handleChange(index, 'city', e.target.value)}
                    size="small"
                    helperText={donation.city ? '✓ Auto-filled' : ''}
                  />
                </Grid>
                {/* State - Auto-filled from PIN */}
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="State"
                    value={donation.state}
                    onChange={(e) => handleChange(index, 'state', e.target.value)}
                    size="small"
                    helperText={donation.state ? '✓ Auto-filled' : ''}
                  />
                </Grid>
                {/* Donation Type */}
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    select
                    label="Donation Type *"
                    value={donation.donation_type || 'cash'}
                    onChange={(e) => handleChange(index, 'donation_type', e.target.value)}
                    required
                    size="small"
                  >
                    <MenuItem value="cash">Cash</MenuItem>
                    <MenuItem value="in_kind">In-Kind</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label={donation.donation_type === 'in_kind' ? "Assessed Value (₹)" : "Amount (₹)"}
                    type="number"
                    value={donation.amount}
                    onChange={(e) => handleChange(index, 'amount', e.target.value)}
                    required
                    size="small"
                    inputProps={{ min: 1, step: 0.01 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2.5}>
                  <TextField
                    fullWidth
                    select
                    label="Category"
                    value={donation.category}
                    onChange={(e) => handleChange(index, 'category', e.target.value)}
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
                {/* Payment Mode - only for cash donations */}
                {donation.donation_type === 'cash' && (
                  <Grid item xs={12} sm={6} md={2.5}>
                    <TextField
                      fullWidth
                      select
                      label="Payment Mode *"
                      value={donation.payment_mode}
                      onChange={(e) => handleChange(index, 'payment_mode', e.target.value)}
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
                )}
                {/* Bank Account - for non-cash payments */}
                {donation.donation_type === 'cash' && 
                 donation.payment_mode !== 'Cash' && 
                 bankAccounts.length > 0 && (
                  <Grid item xs={12} sm={6} md={2.5}>
                    <TextField
                      fullWidth
                      select
                      label="Bank Account *"
                      value={donation.bank_account_id || ''}
                      onChange={(e) => handleChange(index, 'bank_account_id', e.target.value)}
                      required
                      size="small"
                      helperText="Select bank account"
                    >
                      {bankAccounts.map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                          {account.name} ({account.bank_name}) {account.is_primary ? '(Primary)' : ''}
                        </MenuItem>
                      ))}
                    </TextField>
                  </Grid>
                )}
                
                {/* Payment-specific fields based on payment_mode */}
                {donation.payment_mode === 'UPI' && (
                  <>
                    <Grid item xs={12} sm={6} md={3}>
                      <TextField
                        fullWidth
                        label="Sender UPI ID"
                        value={donation.sender_upi_id || ''}
                        onChange={(e) => handleChange(index, 'sender_upi_id', e.target.value)}
                        size="small"
                        placeholder="9876543210@paytm"
                        helperText="From SMS notification"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <TextField
                        fullWidth
                        label="UPI Reference Number"
                        value={donation.upi_reference_number || ''}
                        onChange={(e) => handleChange(index, 'upi_reference_number', e.target.value)}
                        size="small"
                        placeholder="UTR/RRN from SMS"
                        helperText="Transaction reference"
                      />
                    </Grid>
                  </>
                )}
                
                {donation.payment_mode === 'Cheque' && (
                  <>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Cheque Number *"
                        value={donation.cheque_number || ''}
                        onChange={(e) => handleChange(index, 'cheque_number', e.target.value)}
                        required
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Cheque Date *"
                        type="date"
                        value={donation.cheque_date || ''}
                        onChange={(e) => handleChange(index, 'cheque_date', e.target.value)}
                        required
                        size="small"
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Bank Name *"
                        value={donation.cheque_bank_name || ''}
                        onChange={(e) => handleChange(index, 'cheque_bank_name', e.target.value)}
                        required
                        size="small"
                        placeholder="e.g., SBI, HDFC"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Branch"
                        value={donation.cheque_branch || ''}
                        onChange={(e) => handleChange(index, 'cheque_branch', e.target.value)}
                        size="small"
                        placeholder="Branch name"
                      />
                    </Grid>
                  </>
                )}
                
                {donation.payment_mode === 'Online' && (
                  <>
                    <Grid item xs={12} sm={6} md={3}>
                      <TextField
                        fullWidth
                        label="UTR Number *"
                        value={donation.utr_number || ''}
                        onChange={(e) => handleChange(index, 'utr_number', e.target.value)}
                        required
                        size="small"
                        placeholder="Unique Transfer Reference"
                        helperText="UTR from bank"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <TextField
                        fullWidth
                        label="Payer Name"
                        value={donation.payer_name || ''}
                        onChange={(e) => handleChange(index, 'payer_name', e.target.value)}
                        size="small"
                        placeholder="Name of person who made transfer"
                        helperText="May be different from devotee"
                      />
                    </Grid>
                  </>
                )}
                
                {/* Anonymous Checkbox */}
                <Grid item xs={12} sm={6} md={1.5}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={donation.is_anonymous || false}
                        onChange={(e) => handleChange(index, 'is_anonymous', e.target.checked)}
                        size="small"
                      />
                    }
                    label="Anonymous"
                  />
                </Grid>
              </Grid>
              
              {/* In-Kind Donation Fields - shown only when donation_type is in_kind */}
              <Collapse in={donation.donation_type === 'in_kind'}>
                <Box sx={{ mt: 2, p: 2, bgcolor: '#f0f0f0', borderRadius: 1 }}>
                  <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    In-Kind Donation Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <TextField
                        fullWidth
                        select
                        label="In-Kind Subtype *"
                        value={donation.inkind_subtype || ''}
                        onChange={(e) => handleChange(index, 'inkind_subtype', e.target.value)}
                        required={donation.donation_type === 'in_kind'}
                        size="small"
                      >
                        <MenuItem value="inventory">Inventory (Rice, Dal, etc.)</MenuItem>
                        <MenuItem value="event_sponsorship">Event Sponsorship</MenuItem>
                        <MenuItem value="asset">Asset (Gold, Silver, etc.)</MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <TextField
                        fullWidth
                        label="Item Name *"
                        value={donation.item_name || ''}
                        onChange={(e) => handleChange(index, 'item_name', e.target.value)}
                        required={donation.donation_type === 'in_kind'}
                        size="small"
                        placeholder="e.g., Rice, Gold, Flowers"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Quantity"
                        type="number"
                        value={donation.quantity || ''}
                        onChange={(e) => handleChange(index, 'quantity', e.target.value)}
                        size="small"
                        inputProps={{ min: 0, step: 0.01 }}
                        required={donation.inkind_subtype === 'inventory'}
                        helperText={donation.inkind_subtype === 'event_sponsorship' ? 'Optional for sponsorship' : ''}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Unit"
                        value={donation.unit || ''}
                        onChange={(e) => handleChange(index, 'unit', e.target.value)}
                        size="small"
                        placeholder="kg, pieces, etc."
                        required={donation.inkind_subtype === 'inventory'}
                        helperText={donation.inkind_subtype === 'event_sponsorship' ? 'Optional for sponsorship' : ''}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={2}>
                      <TextField
                        fullWidth
                        label="Assessed Value (₹)"
                        type="number"
                        value={donation.value_assessed || donation.amount || ''}
                        onChange={(e) => handleChange(index, 'value_assessed', e.target.value)}
                        size="small"
                        inputProps={{ min: 0, step: 0.01 }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Item Description"
                        value={donation.item_description || ''}
                        onChange={(e) => handleChange(index, 'item_description', e.target.value)}
                        size="small"
                        multiline
                        rows={2}
                        placeholder="Additional details about the item"
                      />
                    </Grid>
                  </Grid>
                </Box>
              </Collapse>
            </Paper>
          ))}

          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            <Button
              type="submit"
              variant="contained"
              startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
              disabled={saving}
              size="large"
            >
              {saving ? 'Saving...' : 'Save All Donations'}
            </Button>
            <Button
              variant="outlined"
              onClick={() => setDonations([{ devotee_name: '', devotee_phone: '', pincode: '', city: '', state: '', country: 'India', amount: '', category: '', payment_mode: 'Cash' }])}
            >
              Clear All
            </Button>
          </Box>
        </Box>
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              Donation List
            </Typography>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : donationList.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Devotee</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Payment</TableCell>
                      <TableCell>Receipt</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {donationList.slice(0, 10).map((donation) => (
                      <TableRow key={donation.id}>
                        <TableCell>{new Date(donation.donation_date || donation.created_at).toLocaleDateString()}</TableCell>
                        <TableCell>{donation.devotee?.name || 'N/A'}</TableCell>
                        <TableCell>{formatCurrency(donation.amount)}</TableCell>
                        <TableCell>
                          <Chip label={donation.category?.name || 'General'} size="small" />
                        </TableCell>
                        <TableCell>{donation.payment_mode}</TableCell>
                        <TableCell>{donation.receipt_number || 'N/A'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="text.secondary" sx={{ p: 2 }}>
                No donations recorded yet
              </Typography>
            )}
          </Box>
        )}
      </Paper>

    </Layout>
  );
}

export default Donations;
