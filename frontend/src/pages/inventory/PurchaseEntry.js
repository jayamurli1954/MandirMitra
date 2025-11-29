import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

function PurchaseEntry() {
  const [items, setItems] = useState([]);
  const [stores, setStores] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    movement_date: new Date(),
    item_id: '',
    store_id: '',
    quantity: '',
    unit_price: '',
    reference_number: '',
    vendor_id: '',
    notes: ''
  });

  useEffect(() => {
    fetchItems();
    fetchStores();
    fetchVendors();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await api.get('/api/v1/inventory/items/', { params: { is_active: true } });
      setItems(response.data || []);
    } catch (err) {
      console.error('Error fetching items:', err);
    }
  };

  const fetchStores = async () => {
    try {
      const response = await api.get('/api/v1/inventory/stores/', { params: { is_active: true } });
      setStores(response.data || []);
    } catch (err) {
      console.error('Error fetching stores:', err);
    }
  };

  const fetchVendors = async () => {
    try {
      const response = await api.get('/api/v1/vendors/');
      setVendors(response.data || []);
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
        movement_date: formData.movement_date.toISOString().split('T')[0],
        quantity: parseFloat(formData.quantity),
        unit_price: parseFloat(formData.unit_price),
        movement_type: 'purchase'
      };

      const response = await api.post('/api/v1/inventory/movements/purchase/', purchaseData);
      setSuccess(`Purchase recorded successfully! Movement: ${response.data.movement_number}`);
      
      // Reset form
      setFormData({
        movement_date: new Date(),
        item_id: '',
        store_id: '',
        quantity: '',
        unit_price: '',
        reference_number: '',
        vendor_id: '',
        notes: ''
      });
      
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record purchase');
    } finally {
      setSaving(false);
    }
  };

  const selectedItem = items.find(item => item.id === parseInt(formData.item_id));
  const totalValue = formData.quantity && formData.unit_price 
    ? parseFloat(formData.quantity) * parseFloat(formData.unit_price) 
    : 0;

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Purchase Entry
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

        <Paper sx={{ p: 3 }}>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Purchase Date *"
                    value={formData.movement_date}
                    onChange={(newValue) => setFormData({ ...formData, movement_date: newValue })}
                    renderInput={(params) => <TextField {...params} fullWidth required />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Store *"
                  value={formData.store_id}
                  onChange={(e) => setFormData({ ...formData, store_id: e.target.value })}
                  required
                >
                  {stores.map((store) => (
                    <MenuItem key={store.id} value={store.id}>
                      {store.code} - {store.name}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Item *"
                  value={formData.item_id}
                  onChange={(e) => setFormData({ ...formData, item_id: e.target.value })}
                  required
                >
                  {items.map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.code} - {item.name} ({item.unit})
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              {selectedItem && (
                <Grid item xs={12} sm={6}>
                  <Alert severity="info" sx={{ py: 0.5 }}>
                    Category: {selectedItem.category} | Standard Cost: ₹{selectedItem.standard_cost}
                  </Alert>
                </Grid>
              )}
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Quantity *"
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  required
                  inputProps={{ min: 0, step: 0.01 }}
                  helperText={selectedItem ? `Unit: ${selectedItem.unit}` : ''}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Unit Price (₹) *"
                  type="number"
                  value={formData.unit_price}
                  onChange={(e) => setFormData({ ...formData, unit_price: e.target.value })}
                  required
                  inputProps={{ min: 0, step: 0.01 }}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Total Value (₹)"
                  value={totalValue.toFixed(2)}
                  InputProps={{ readOnly: true }}
                  sx={{ bgcolor: '#f5f5f5' }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Bill/Reference Number"
                  value={formData.reference_number}
                  onChange={(e) => setFormData({ ...formData, reference_number: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Vendor (Optional)"
                  value={formData.vendor_id}
                  onChange={(e) => setFormData({ ...formData, vendor_id: e.target.value })}
                >
                  <MenuItem value="">None</MenuItem>
                  {vendors.map((vendor) => (
                    <MenuItem key={vendor.id} value={vendor.id}>
                      {vendor.name}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                  disabled={saving}
                  fullWidth
                >
                  {saving ? 'Recording Purchase...' : 'Record Purchase'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
    </Layout>
  );
}

export default PurchaseEntry;




