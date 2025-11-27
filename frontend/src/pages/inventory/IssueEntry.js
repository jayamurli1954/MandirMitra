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

function IssueEntry() {
  const [items, setItems] = useState([]);
  const [stores, setStores] = useState([]);
  const [stockBalances, setStockBalances] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    movement_date: new Date(),
    item_id: '',
    store_id: '',
    quantity: '',
    issued_to: '',
    purpose: '',
    notes: ''
  });

  useEffect(() => {
    fetchItems();
    fetchStores();
  }, []);

  useEffect(() => {
    if (formData.item_id && formData.store_id) {
      fetchStockBalance();
    }
  }, [formData.item_id, formData.store_id]);

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

  const fetchStockBalance = async () => {
    try {
      const response = await api.get('/api/v1/inventory/stock-balances/', {
        params: {
          item_id: formData.item_id,
          store_id: formData.store_id
        }
      });
      setStockBalances(response.data || []);
    } catch (err) {
      console.error('Error fetching stock balance:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const issueData = {
        ...formData,
        movement_date: formData.movement_date.toISOString().split('T')[0],
        quantity: parseFloat(formData.quantity),
        unit_price: 0, // Will be calculated from stock balance
        movement_type: 'issue'
      };

      const response = await api.post('/api/v1/inventory/movements/issue/', issueData);
      setSuccess(`Issue recorded successfully! Movement: ${response.data.movement_number}`);
      
      // Reset form
      setFormData({
        movement_date: new Date(),
        item_id: '',
        store_id: '',
        quantity: '',
        issued_to: '',
        purpose: '',
        notes: ''
      });
      setStockBalances([]);
      
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record issue');
    } finally {
      setSaving(false);
    }
  };

  const selectedItem = items.find(item => item.id === parseInt(formData.item_id));
  const currentStock = stockBalances.find(
    bal => bal.item_id === parseInt(formData.item_id) && bal.store_id === parseInt(formData.store_id)
  );

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Issue Entry (Consumption)
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
                    label="Issue Date *"
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
              {currentStock && (
                <Grid item xs={12} sm={6}>
                  <Alert 
                    severity={currentStock.quantity > 0 ? "info" : "warning"}
                    sx={{ py: 0.5 }}
                  >
                    Available Stock: {currentStock.quantity} {selectedItem?.unit || ''} 
                    (Value: ₹{currentStock.value.toFixed(2)})
                  </Alert>
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Quantity *"
                  type="number"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  required
                  inputProps={{ min: 0, step: 0.01 }}
                  helperText={selectedItem ? `Unit: ${selectedItem.unit}` : ''}
                  error={currentStock && parseFloat(formData.quantity) > currentStock.quantity}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Issued To *"
                  value={formData.issued_to}
                  onChange={(e) => setFormData({ ...formData, issued_to: e.target.value })}
                  required
                  placeholder="Person/Department name"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Purpose *"
                  value={formData.purpose}
                  onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                  required
                >
                  <MenuItem value="Daily Pooja">Daily Pooja</MenuItem>
                  <MenuItem value="Annadanam">Annadanam</MenuItem>
                  <MenuItem value="Festival">Festival</MenuItem>
                  <MenuItem value="Maintenance">Maintenance</MenuItem>
                  <MenuItem value="Cleaning">Cleaning</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
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
                  disabled={saving || (currentStock && parseFloat(formData.quantity) > currentStock.quantity)}
                  fullWidth
                >
                  {saving ? 'Recording Issue...' : 'Record Issue'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
    </Layout>
  );
}

export default IssueEntry;


