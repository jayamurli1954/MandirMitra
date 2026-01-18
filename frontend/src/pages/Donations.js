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
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../components/Layout';
import api from '../services/api';

function Donations() {
  const [donations, setDonations] = useState([
    { devotee_name: '', devotee_phone: '', amount: '', category: '', payment_mode: 'Cash' }
  ]);
  const [categories, setCategories] = useState([]);
  const [devotees, setDevotees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [donationList, setDonationList] = useState([]);

  const paymentModes = ['Cash', 'Card', 'UPI', 'Cheque', 'Online'];

  useEffect(() => {
    fetchCategories();
    fetchDevotees();
    fetchDonations();
  }, []);

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
      setDonations([...donations, { devotee_name: '', devotee_phone: '', amount: '', category: '', payment_mode: 'Cash' }]);
    }
  };

  const handleRemoveRow = (index) => {
    if (donations.length > 1) {
      setDonations(donations.filter((_, i) => i !== index));
    }
  };

  const handleChange = (index, field, value) => {
    const updated = [...donations];
    updated[index][field] = value;
    
    // Auto-fill devotee name if phone matches
    if (field === 'devotee_phone' && value) {
      const devotee = devotees.find(d => d.phone === value);
      if (devotee) {
        updated[index].devotee_name = devotee.name || '';
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
        d.devotee_name && d.devotee_phone && d.amount && d.category
      );

      if (validDonations.length === 0) {
        setError('Please fill at least one donation entry');
        setSaving(false);
        return;
      }

      // Save each donation
      const promises = validDonations.map(donation => 
        api.post('/api/v1/donations', {
          devotee_name: donation.devotee_name,
          devotee_phone: donation.devotee_phone,
          amount: parseFloat(donation.amount),
          category: donation.category,
          payment_mode: donation.payment_mode,
        })
      );

      await Promise.all(promises);
      
      setSuccess(`Successfully recorded ${validDonations.length} donation(s)!`);
      setDonations([{ devotee_name: '', devotee_phone: '', amount: '', category: '', payment_mode: 'Cash' }]);
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

      <Paper sx={{ p: 3, mt: 2 }}>
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
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    fullWidth
                    label="Devotee Name"
                    value={donation.devotee_name}
                    onChange={(e) => handleChange(index, 'devotee_name', e.target.value)}
                    required
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="Phone"
                    value={donation.devotee_phone}
                    onChange={(e) => handleChange(index, 'devotee_phone', e.target.value)}
                    required
                    size="small"
                    inputProps={{ maxLength: 10 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <TextField
                    fullWidth
                    label="Amount (₹)"
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
                <Grid item xs={12} sm={6} md={2.5}>
                  <TextField
                    fullWidth
                    select
                    label="Payment Mode"
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
              </Grid>
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
              onClick={() => setDonations([{ devotee_name: '', devotee_phone: '', amount: '', category: '', payment_mode: 'Cash' }])}
            >
              Clear All
            </Button>
          </Box>
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
          Recent Donations
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
      </Paper>
    </Layout>
  );
}

export default Donations;
