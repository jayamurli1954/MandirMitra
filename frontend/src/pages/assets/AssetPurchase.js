import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
  Paper,
  Card,
  CardContent
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import axios from 'axios';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const AssetPurchase = () => {
  const [categories, setCategories] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [formData, setFormData] = useState({
    asset_number: '',
    name: '',
    description: '',
    category_id: '',
    asset_type: 'fixed',
    location: '',
    tag_number: '',
    serial_number: '',
    purchase_date: new Date(),
    amount: 0,
    payment_mode: 'cash',
    vendor_id: '',
    reference_number: '',
    // Depreciation details
    depreciation_method: 'straight_line',
    useful_life_years: 0,
    depreciation_rate_percent: 0,
    salvage_value: 0,
    is_depreciable: true
  });

  useEffect(() => {
    fetchCategories();
    fetchVendors();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/v1/assets/categories/');
      setCategories(response.data);
    } catch (err) {
      setError('Failed to load categories');
    }
  };

  const fetchVendors = async () => {
    try {
      const response = await axios.get('/api/v1/vendors/');
      setVendors(response.data);
    } catch (err) {
      console.error('Error fetching vendors:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const purchaseData = {
        ...formData,
        purchase_date: formData.purchase_date.toISOString().split('T')[0],
        amount: parseFloat(formData.amount)
      };

      const response = await axios.post('/api/v1/assets/purchase/', purchaseData);
      setSuccess(`Asset purchased successfully! Asset: ${response.data.asset_number}`);
      
      // Reset form
      setFormData({
        asset_number: '',
        name: '',
        description: '',
        category_id: '',
        asset_type: 'fixed',
        location: '',
        tag_number: '',
        serial_number: '',
        purchase_date: new Date(),
        amount: 0,
        payment_mode: 'cash',
        vendor_id: '',
        reference_number: '',
        depreciation_method: 'straight_line',
        useful_life_years: 0,
        depreciation_rate_percent: 0,
        salvage_value: 0,
        is_depreciable: true
      });
      
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record asset purchase');
    } finally {
      setSaving(false);
    }
  };

  const selectedCategory = categories.find(cat => cat.id === parseInt(formData.category_id));

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Asset Purchase
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2 }}>Asset Details</Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Asset Number *"
                value={formData.asset_number}
                onChange={(e) => setFormData({ ...formData, asset_number: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Asset Name *"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Category *"
                value={formData.category_id}
                onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                required
              >
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Asset Type *"
                value={formData.asset_type}
                onChange={(e) => setFormData({ ...formData, asset_type: e.target.value })}
                required
              >
                <MenuItem value="fixed">Fixed Asset</MenuItem>
                <MenuItem value="movable">Movable Asset</MenuItem>
                <MenuItem value="precious">Precious Asset</MenuItem>
                <MenuItem value="intangible">Intangible Asset</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Location"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tag Number"
                value={formData.tag_number}
                onChange={(e) => setFormData({ ...formData, tag_number: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Serial Number"
                value={formData.serial_number}
                onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="Purchase Date *"
                  value={formData.purchase_date}
                  onChange={(newValue) => setFormData({ ...formData, purchase_date: newValue })}
                  renderInput={(params) => <TextField {...params} fullWidth required />}
                />
              </LocalizationProvider>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2, mt: 2 }}>Purchase Details</Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Purchase Amount *"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Payment Mode *"
                value={formData.payment_mode}
                onChange={(e) => setFormData({ ...formData, payment_mode: e.target.value })}
                required
              >
                <MenuItem value="cash">Cash</MenuItem>
                <MenuItem value="bank">Bank Transfer</MenuItem>
                <MenuItem value="cheque">Cheque</MenuItem>
                <MenuItem value="payable">Payable (Credit)</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Vendor"
                value={formData.vendor_id}
                onChange={(e) => setFormData({ ...formData, vendor_id: e.target.value })}
              >
                <MenuItem value="">Select Vendor</MenuItem>
                {vendors.map((vendor) => (
                  <MenuItem key={vendor.id} value={vendor.id}>
                    {vendor.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Reference Number"
                value={formData.reference_number}
                onChange={(e) => setFormData({ ...formData, reference_number: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2, mt: 2 }}>Depreciation Details</Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Depreciation Method"
                value={formData.depreciation_method}
                onChange={(e) => setFormData({ ...formData, depreciation_method: e.target.value })}
              >
                <MenuItem value="straight_line">Straight Line</MenuItem>
                <MenuItem value="wdv">Written Down Value</MenuItem>
                <MenuItem value="double_declining">Double Declining</MenuItem>
                <MenuItem value="declining_balance">Declining Balance</MenuItem>
                <MenuItem value="units_of_production">Units of Production</MenuItem>
                <MenuItem value="annuity">Annuity</MenuItem>
                <MenuItem value="depletion">Depletion</MenuItem>
                <MenuItem value="sinking_fund">Sinking Fund</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Useful Life (Years)"
                value={formData.useful_life_years}
                onChange={(e) => setFormData({ ...formData, useful_life_years: parseFloat(e.target.value) || 0 })}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Depreciation Rate (%)"
                value={formData.depreciation_rate_percent}
                onChange={(e) => setFormData({ ...formData, depreciation_rate_percent: parseFloat(e.target.value) || 0 })}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Salvage Value"
                value={formData.salvage_value}
                onChange={(e) => setFormData({ ...formData, salvage_value: parseFloat(e.target.value) || 0 })}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={saving}
                sx={{ mt: 2 }}
              >
                {saving ? <CircularProgress size={24} /> : 'Record Purchase'}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default AssetPurchase;


