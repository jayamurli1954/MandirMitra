import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  IconButton,
  Alert,
  CircularProgress,
  MenuItem,
  Chip
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';

const AssetMaster = () => {
  const [categories, setCategories] = useState([]);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [categoryDialogOpen, setCategoryDialogOpen] = useState(false);
  const [assetDialogOpen, setAssetDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [editingAsset, setEditingAsset] = useState(null);
  
  const [categoryForm, setCategoryForm] = useState({
    code: '',
    name: '',
    description: '',
    default_depreciation_method: 'straight_line',
    default_useful_life_years: 0,
    default_depreciation_rate_percent: 0,
    is_depreciable: true
  });

  const [assetForm, setAssetForm] = useState({
    asset_number: '',
    name: '',
    description: '',
    category_id: '',
    asset_type: 'fixed',
    location: '',
    tag_number: '',
    serial_number: '',
    purchase_date: new Date().toISOString().split('T')[0],
    original_cost: 0,
    useful_life_years: 0,
    depreciation_rate_percent: 0,
    salvage_value: 0,
    is_depreciable: true,
    depreciation_method: 'straight_line'
  });

  useEffect(() => {
    fetchCategories();
    fetchAssets();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/v1/assets/categories/');
      setCategories(response.data);
    } catch (err) {
      setError('Failed to load categories');
    }
  };

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/assets/');
      setAssets(response.data);
    } catch (err) {
      setError('Failed to load assets');
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCategory) {
        await axios.put(`/api/v1/assets/categories/${editingCategory.id}`, categoryForm);
        setSuccess('Category updated successfully');
      } else {
        await axios.post('/api/v1/assets/categories/', categoryForm);
        setSuccess('Category created successfully');
      }
      setCategoryDialogOpen(false);
      setEditingCategory(null);
      setCategoryForm({
        code: '',
        name: '',
        description: '',
        default_depreciation_method: 'straight_line',
        default_useful_life_years: 0,
        default_depreciation_rate_percent: 0,
        is_depreciable: true
      });
      fetchCategories();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save category');
    }
  };

  const handleAssetEdit = (asset) => {
    setEditingAsset(asset);
    setAssetForm({
      asset_number: asset.asset_number,
      name: asset.name,
      description: asset.description || '',
      category_id: asset.category_id,
      asset_type: asset.asset_type,
      location: asset.location || '',
      tag_number: asset.tag_number || '',
      serial_number: asset.serial_number || '',
      purchase_date: asset.purchase_date,
      original_cost: asset.original_cost,
      useful_life_years: asset.useful_life_years || 0,
      depreciation_rate_percent: asset.depreciation_rate_percent || 0,
      salvage_value: asset.salvage_value || 0,
      is_depreciable: asset.is_depreciable,
      depreciation_method: asset.depreciation_method || 'straight_line'
    });
    setAssetDialogOpen(true);
  };

  const handleAssetUpdate = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/api/v1/assets/${editingAsset.id}`, assetForm);
      setSuccess('Asset updated successfully');
      setAssetDialogOpen(false);
      setEditingAsset(null);
      fetchAssets();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update asset');
    }
  };

  const handleAssetDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
      try {
        await axios.delete(`/api/v1/assets/${id}`);
        setSuccess('Asset deleted successfully');
        fetchAssets();
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to delete asset');
      }
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Asset Master
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setEditingCategory(null);
            setCategoryForm({
              code: '',
              name: '',
              description: '',
              default_depreciation_method: 'straight_line',
              default_useful_life_years: 0,
              default_depreciation_rate_percent: 0,
              is_depreciable: true
            });
            setCategoryDialogOpen(true);
          }}
        >
          Add Category
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

      {/* Categories Section */}
      <Paper sx={{ mb: 4 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Asset Categories</Typography>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Depreciation Method</TableCell>
                <TableCell>Useful Life (Years)</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {categories.map((category) => (
                <TableRow key={category.id}>
                  <TableCell>{category.code}</TableCell>
                  <TableCell>{category.name}</TableCell>
                  <TableCell>{category.default_depreciation_method}</TableCell>
                  <TableCell>{category.default_useful_life_years}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setEditingCategory(category);
                        setCategoryForm(category);
                        setCategoryDialogOpen(true);
                      }}
                    >
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Assets Section */}
      <Paper>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Assets</Typography>
        </Box>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Asset Number</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Cost</TableCell>
                  <TableCell>Book Value</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {assets.map((asset) => (
                  <TableRow key={asset.id}>
                    <TableCell>{asset.asset_number}</TableCell>
                    <TableCell>{asset.name}</TableCell>
                    <TableCell>{asset.category?.name || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip label={asset.asset_type} size="small" />
                    </TableCell>
                    <TableCell>₹{asset.original_cost?.toLocaleString() || 0}</TableCell>
                    <TableCell>₹{asset.current_book_value?.toLocaleString() || 0}</TableCell>
                    <TableCell>
                      <Chip label={asset.status} size="small" color={asset.status === 'active' ? 'success' : 'default'} />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleAssetEdit(asset)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleAssetDelete(asset.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Category Dialog */}
      <Dialog open={categoryDialogOpen} onClose={() => setCategoryDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleCategorySubmit}>
          <DialogTitle>{editingCategory ? 'Edit Category' : 'Add Category'}</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Code"
                  value={categoryForm.code}
                  onChange={(e) => setCategoryForm({ ...categoryForm, code: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Name"
                  value={categoryForm.name}
                  onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={categoryForm.description}
                  onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })}
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Depreciation Method"
                  value={categoryForm.default_depreciation_method}
                  onChange={(e) => setCategoryForm({ ...categoryForm, default_depreciation_method: e.target.value })}
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
                  value={categoryForm.default_useful_life_years}
                  onChange={(e) => setCategoryForm({ ...categoryForm, default_useful_life_years: parseFloat(e.target.value) || 0 })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCategoryDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Save</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Asset Edit Dialog */}
      <Dialog open={assetDialogOpen} onClose={() => setAssetDialogOpen(false)} maxWidth="md" fullWidth>
        <form onSubmit={handleAssetUpdate}>
          <DialogTitle>Edit Asset</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Asset Number"
                  value={assetForm.asset_number}
                  disabled
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Name"
                  value={assetForm.name}
                  onChange={(e) => setAssetForm({ ...assetForm, name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={assetForm.description}
                  onChange={(e) => setAssetForm({ ...assetForm, description: e.target.value })}
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Location"
                  value={assetForm.location}
                  onChange={(e) => setAssetForm({ ...assetForm, location: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Tag Number"
                  value={assetForm.tag_number}
                  onChange={(e) => setAssetForm({ ...assetForm, tag_number: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAssetDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Update</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Container>
  );
};

export default AssetMaster;




