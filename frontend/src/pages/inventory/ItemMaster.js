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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  Alert,
  CircularProgress,
  IconButton,
  Chip,
  Grid,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Layout from '../../components/Layout';
import api from '../../services/api';

const ITEM_CATEGORIES = [
  { value: 'pooja_material', label: 'Pooja Material' },
  { value: 'grocery', label: 'Grocery & Annadanam' },
  { value: 'cleaning', label: 'Cleaning Supplies' },
  { value: 'maintenance', label: 'Maintenance Items' },
  { value: 'general', label: 'General' }
];

const UNITS = [
  { value: 'kg', label: 'Kilogram (kg)' },
  { value: 'gram', label: 'Gram' },
  { value: 'litre', label: 'Litre' },
  { value: 'ml', label: 'Millilitre (ml)' },
  { value: 'piece', label: 'Piece' },
  { value: 'packet', label: 'Packet' },
  { value: 'box', label: 'Box' },
  { value: 'bottle', label: 'Bottle' },
  { value: 'bag', label: 'Bag' }
];

function ItemMaster() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    category: 'general',
    unit: 'piece',
    reorder_level: 0,
    reorder_quantity: 0,
    standard_cost: 0,
    hsn_code: '',
    gst_rate: 0
  });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/inventory/items/');
      setItems(response.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        code: item.code,
        name: item.name,
        description: item.description || '',
        category: item.category,
        unit: item.unit,
        reorder_level: item.reorder_level || 0,
        reorder_quantity: item.reorder_quantity || 0,
        standard_cost: item.standard_cost || 0,
        hsn_code: item.hsn_code || '',
        gst_rate: item.gst_rate || 0
      });
    } else {
      setEditingItem(null);
      setFormData({
        code: '',
        name: '',
        description: '',
        category: 'general',
        unit: 'piece',
        reorder_level: 0,
        reorder_quantity: 0,
        standard_cost: 0,
        hsn_code: '',
        gst_rate: 0
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingItem(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      if (editingItem) {
        // Update existing item
        await api.put(`/api/v1/inventory/items/${editingItem.id}`, formData);
        setSuccess('Item updated successfully');
      } else {
        // Create new item
        await api.post('/api/v1/inventory/items/', formData);
        setSuccess('Item created successfully');
      }
      handleCloseDialog();
      fetchItems();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save item');
    }
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm('Are you sure you want to delete this item?')) {
      return;
    }

    try {
      await api.delete(`/api/v1/inventory/items/${itemId}`);
      setSuccess('Item deleted successfully');
      fetchItems();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete item');
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      pooja_material: '#4CAF50',
      grocery: '#FF9800',
      cleaning: '#2196F3',
      maintenance: '#9C27B0',
      general: '#757575'
    };
    return colors[category] || '#757575';
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
            Item Master
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Item
          </Button>
        </Box>

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

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Code</strong></TableCell>
                  <TableCell><strong>Name</strong></TableCell>
                  <TableCell><strong>Category</strong></TableCell>
                  <TableCell><strong>Unit</strong></TableCell>
                  <TableCell align="right"><strong>Reorder Level</strong></TableCell>
                  <TableCell align="right"><strong>Standard Cost</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No items found. Click "Add Item" to create one.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.code}</TableCell>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>
                        <Chip
                          label={ITEM_CATEGORIES.find(c => c.value === item.category)?.label || item.category}
                          size="small"
                          sx={{
                            bgcolor: getCategoryColor(item.category),
                            color: 'white'
                          }}
                        />
                      </TableCell>
                      <TableCell>{UNITS.find(u => u.value === item.unit)?.label || item.unit}</TableCell>
                      <TableCell align="right">{item.reorder_level} {item.unit}</TableCell>
                      <TableCell align="right">₹{item.standard_cost}</TableCell>
                      <TableCell>
                        <Chip
                          label={item.is_active ? 'Active' : 'Inactive'}
                          color={item.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(item)}
                          color="primary"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handleDelete(item.id)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {editingItem ? 'Edit Item' : 'Add New Item'}
          </DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Item Code *"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    required
                    disabled={!!editingItem}
                    helperText="Unique code for the item (e.g., ITM001)"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Item Name *"
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
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    required
                  >
                    {ITEM_CATEGORIES.map((cat) => (
                      <MenuItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Unit *"
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                    required
                  >
                    {UNITS.map((unit) => (
                      <MenuItem key={unit.value} value={unit.value}>
                        {unit.label}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Reorder Level"
                    type="number"
                    value={formData.reorder_level}
                    onChange={(e) => setFormData({ ...formData, reorder_level: parseFloat(e.target.value) || 0 })}
                    inputProps={{ min: 0, step: 0.01 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Reorder Quantity"
                    type="number"
                    value={formData.reorder_quantity}
                    onChange={(e) => setFormData({ ...formData, reorder_quantity: parseFloat(e.target.value) || 0 })}
                    inputProps={{ min: 0, step: 0.01 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Standard Cost (₹)"
                    type="number"
                    value={formData.standard_cost}
                    onChange={(e) => setFormData({ ...formData, standard_cost: parseFloat(e.target.value) || 0 })}
                    inputProps={{ min: 0, step: 0.01 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="HSN Code"
                    value={formData.hsn_code}
                    onChange={(e) => setFormData({ ...formData, hsn_code: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="GST Rate (%)"
                    type="number"
                    value={formData.gst_rate}
                    onChange={(e) => setFormData({ ...formData, gst_rate: parseFloat(e.target.value) || 0 })}
                    inputProps={{ min: 0, max: 100, step: 0.01 }}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Cancel</Button>
              <Button type="submit" variant="contained">
                {editingItem ? 'Update' : 'Create'}
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default ItemMaster;

