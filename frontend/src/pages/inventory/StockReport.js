import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  Grid,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import Layout from '../../components/Layout';
import api from '../../services/api';

function StockReport() {
  const [stockBalances, setStockBalances] = useState([]);
  const [items, setItems] = useState([]);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    store_id: '',
    item_id: ''
  });

  useEffect(() => {
    fetchItems();
    fetchStores();
    fetchStockBalances();
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

  const fetchStockBalances = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.store_id) params.store_id = filters.store_id;
      if (filters.item_id) params.item_id = filters.item_id;
      
      const response = await api.get('/api/v1/inventory/stock-balances/', { params });
      setStockBalances(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load stock balances');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const handleSearch = () => {
    fetchStockBalances();
  };

  const totalValue = stockBalances.reduce((sum, bal) => sum + bal.value, 0);

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Stock Report
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                select
                label="Filter by Store"
                value={filters.store_id}
                onChange={(e) => handleFilterChange('store_id', e.target.value)}
                size="small"
              >
                <MenuItem value="">All Stores</MenuItem>
                {stores.map((store) => (
                  <MenuItem key={store.id} value={store.id}>
                    {store.code} - {store.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                select
                label="Filter by Item"
                value={filters.item_id}
                onChange={(e) => handleFilterChange('item_id', e.target.value)}
                size="small"
              >
                <MenuItem value="">All Items</MenuItem>
                {items.map((item) => (
                  <MenuItem key={item.id} value={item.id}>
                    {item.code} - {item.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
                fullWidth
                sx={{ height: '40px' }}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Stock Table */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Paper>
            <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderBottom: '1px solid #ddd' }}>
              <Typography variant="h6">
                Total Inventory Value: ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(totalValue)}
              </Typography>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Item Code</strong></TableCell>
                    <TableCell><strong>Item Name</strong></TableCell>
                    <TableCell><strong>Store</strong></TableCell>
                    <TableCell align="right"><strong>Quantity</strong></TableCell>
                    <TableCell align="right"><strong>Value (₹)</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {stockBalances.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                        <Typography variant="body2" color="text.secondary">
                          No stock found. Record purchases to see stock balances.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    stockBalances.map((balance) => {
                      const item = items.find(i => i.id === balance.item_id);
                      const isLowStock = item && balance.quantity <= item.reorder_level;
                      
                      return (
                        <TableRow key={balance.id}>
                          <TableCell>{balance.item_code}</TableCell>
                          <TableCell>{balance.item_name}</TableCell>
                          <TableCell>{balance.store_name}</TableCell>
                          <TableCell align="right">
                            {balance.quantity.toFixed(2)} {balance.unit}
                          </TableCell>
                          <TableCell align="right">
                            ₹{new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(balance.value)}
                          </TableCell>
                          <TableCell>
                            {isLowStock ? (
                              <Chip label="Low Stock" color="warning" size="small" />
                            ) : balance.quantity > 0 ? (
                              <Chip label="In Stock" color="success" size="small" />
                            ) : (
                              <Chip label="Out of Stock" color="error" size="small" />
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}
      </Box>
    </Layout>
  );
}

export default StockReport;


