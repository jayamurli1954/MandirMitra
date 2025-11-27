import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Stack,
  Grid,
  CircularProgress,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import api from '../services/api';

function SevaManagement() {
  const [sevas, setSevas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Dialog states
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedSeva, setSelectedSeva] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);

  // Form state
  const [sevaForm, setSevaForm] = useState({
    name_english: '',
    name_kannada: '',
    name_sanskrit: '',
    description: '',
    category: 'pooja',
    amount: '',
    min_amount: '',
    max_amount: '',
    availability: 'daily',
    specific_day: '',
    except_day: '',
    time_slot: '',
    max_bookings_per_day: '',
    advance_booking_days: 30,
    requires_approval: false,
    is_active: true,
    benefits: '',
    instructions: '',
    duration_minutes: '',
    materials_required: ''
  });

  const categories = [
    { value: 'abhisheka', label: 'Abhisheka' },
    { value: 'alankara', label: 'Alankara' },
    { value: 'pooja', label: 'Pooja' },
    { value: 'archana', label: 'Archana' },
    { value: 'vahana_seva', label: 'Vahana Seva' },
    { value: 'special', label: 'Special' },
    { value: 'festival', label: 'Festival' }
  ];

  const availabilityOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekday', label: 'Weekdays Only' },
    { value: 'weekend', label: 'Weekends Only' },
    { value: 'specific_day', label: 'Specific Day Only' },
    { value: 'except_day', label: 'Except Specific Day' },
    { value: 'festival_only', label: 'Festival Only' }
  ];

  const weekDays = [
    { value: 0, label: 'Sunday' },
    { value: 1, label: 'Monday' },
    { value: 2, label: 'Tuesday' },
    { value: 3, label: 'Wednesday' },
    { value: 4, label: 'Thursday' },
    { value: 5, label: 'Friday' },
    { value: 6, label: 'Saturday' }
  ];

  useEffect(() => {
    fetchSevas();
  }, []);

  const fetchSevas = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/sevas/', { params: { is_active: false } }); // Get all sevas including inactive
      setSevas(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load sevas');
      setLoading(false);
    }
  };

  const handleAddNew = () => {
    setIsEditMode(false);
    setSevaForm({
      name_english: '',
      name_kannada: '',
      name_sanskrit: '',
      description: '',
      category: 'pooja',
      amount: '',
      min_amount: '',
      max_amount: '',
      availability: 'daily',
      specific_day: '',
      except_day: '',
      time_slot: '',
      max_bookings_per_day: '',
      advance_booking_days: 30,
      requires_approval: false,
      is_active: true,
      benefits: '',
      instructions: '',
      duration_minutes: ''
    });
    setEditDialogOpen(true);
  };

  const handleEdit = (seva) => {
    setIsEditMode(true);
    setSelectedSeva(seva);
    setSevaForm({
      name_english: seva.name_english || '',
      name_kannada: seva.name_kannada || '',
      name_sanskrit: seva.name_sanskrit || '',
      description: seva.description || '',
      category: seva.category || 'pooja',
      amount: seva.amount || '',
      min_amount: seva.min_amount || '',
      max_amount: seva.max_amount || '',
      availability: seva.availability || 'daily',
      specific_day: seva.specific_day !== null ? seva.specific_day : '',
      except_day: seva.except_day !== null ? seva.except_day : '',
      time_slot: seva.time_slot || '',
      max_bookings_per_day: seva.max_bookings_per_day || '',
      advance_booking_days: seva.advance_booking_days || 30,
      requires_approval: seva.requires_approval || false,
      is_active: seva.is_active !== undefined ? seva.is_active : true,
      benefits: seva.benefits || '',
      instructions: seva.instructions || '',
      duration_minutes: seva.duration_minutes || '',
      materials_required: seva.materials_required || ''
    });
    setEditDialogOpen(true);
  };

  const handleDelete = (seva) => {
    setSelectedSeva(seva);
    setDeleteDialogOpen(true);
  };

  const handleSaveSevaForm = async () => {
    try {
      setError(null);

      // Prepare data
      const data = { ...sevaForm };

      // Convert empty strings to null for optional numeric fields
      if (data.min_amount === '') data.min_amount = null;
      if (data.max_amount === '') data.max_amount = null;
      if (data.specific_day === '') data.specific_day = null;
      if (data.except_day === '') data.except_day = null;
      if (data.max_bookings_per_day === '') data.max_bookings_per_day = null;
      if (data.duration_minutes === '') data.duration_minutes = null;

      if (isEditMode) {
        await api.put(`/api/v1/sevas/${selectedSeva.id}`, data);
        setSuccess('Seva updated successfully!');
      } else {
        await api.post('/api/v1/sevas/', data);
        setSuccess('Seva created successfully!');
      }

      setEditDialogOpen(false);
      fetchSevas();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save seva');
    }
  };

  const handleConfirmDelete = async () => {
    try {
      await api.delete(`/api/v1/sevas/${selectedSeva.id}`);
      setSuccess('Seva deleted successfully!');
      setDeleteDialogOpen(false);
      fetchSevas();

      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to delete seva');
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      abhisheka: '#2E7D32',
      alankara: '#1565C0',
      pooja: '#7B1FA2',
      archana: '#F57C00',
      vahana_seva: '#00796B',
      special: '#C62828',
      festival: '#FF6B35'
    };
    return colors[category] || '#666';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 3, background: 'linear-gradient(135deg, #FF9933 0%, #FF6B35 100%)' }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700, color: '#fff', mb: 0.5 }}>
              🛕 Seva Management
            </Typography>
            <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)' }}>
              Add, edit, or delete temple sevas and services
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddNew}
            sx={{
              bgcolor: '#fff',
              color: '#FF6B35',
              '&:hover': { bgcolor: '#f5f5f5' }
            }}
          >
            Add New Seva
          </Button>
        </Box>
      </Paper>

      {/* Alerts */}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Sevas Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: '#f5f5f5' }}>
              <TableCell sx={{ fontWeight: 600 }}>Seva Name</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>Category</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>Amount</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>Availability</TableCell>
              <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 600 }} align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sevas.map((seva) => (
              <TableRow key={seva.id} hover>
                <TableCell>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {seva.name_english}
                  </Typography>
                  {seva.name_kannada && (
                    <Typography variant="caption" color="text.secondary">
                      {seva.name_kannada}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={seva.category.replace('_', ' ').toUpperCase()}
                    size="small"
                    sx={{
                      bgcolor: getCategoryColor(seva.category),
                      color: '#fff',
                      fontWeight: 600
                    }}
                  />
                </TableCell>
                <TableCell>
                  {seva.min_amount && seva.max_amount ? (
                    <Typography variant="body2">
                      ₹{seva.min_amount} - ₹{seva.max_amount}
                    </Typography>
                  ) : (
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      ₹{seva.amount}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {seva.availability.replace('_', ' ').toUpperCase()}
                  </Typography>
                  {seva.time_slot && (
                    <Typography variant="caption" color="text.secondary">
                      {seva.time_slot}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={seva.is_active ? 'Active' : 'Inactive'}
                    size="small"
                    color={seva.is_active ? 'success' : 'default'}
                  />
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    color="primary"
                    onClick={() => handleEdit(seva)}
                    size="small"
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    color="error"
                    onClick={() => handleDelete(seva)}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {isEditMode ? 'Edit Seva' : 'Add New Seva'}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            {/* Basic Info */}
            <Grid item xs={12} sm={6}>
              <TextField
                label="Seva Name (English) *"
                value={sevaForm.name_english}
                onChange={(e) => setSevaForm({...sevaForm, name_english: e.target.value})}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Seva Name (Kannada)"
                value={sevaForm.name_kannada}
                onChange={(e) => setSevaForm({...sevaForm, name_kannada: e.target.value})}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Seva Name (Sanskrit)"
                value={sevaForm.name_sanskrit}
                onChange={(e) => setSevaForm({...sevaForm, name_sanskrit: e.target.value})}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>Category</InputLabel>
                <Select
                  value={sevaForm.category}
                  onChange={(e) => setSevaForm({...sevaForm, category: e.target.value})}
                  label="Category"
                >
                  {categories.map(cat => (
                    <MenuItem key={cat.value} value={cat.value}>{cat.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Description */}
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={sevaForm.description}
                onChange={(e) => setSevaForm({...sevaForm, description: e.target.value})}
                multiline
                rows={2}
                fullWidth
              />
            </Grid>

            {/* Pricing */}
            <Grid item xs={12} sm={4}>
              <TextField
                label="Fixed Amount *"
                type="number"
                value={sevaForm.amount}
                onChange={(e) => setSevaForm({...sevaForm, amount: parseFloat(e.target.value) || ''})}
                InputProps={{ startAdornment: '₹' }}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Minimum Amount (Optional)"
                type="number"
                value={sevaForm.min_amount}
                onChange={(e) => setSevaForm({...sevaForm, min_amount: parseFloat(e.target.value) || ''})}
                InputProps={{ startAdornment: '₹' }}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Maximum Amount (Optional)"
                type="number"
                value={sevaForm.max_amount}
                onChange={(e) => setSevaForm({...sevaForm, max_amount: parseFloat(e.target.value) || ''})}
                InputProps={{ startAdornment: '₹' }}
                fullWidth
              />
            </Grid>

            {/* Availability */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Availability</InputLabel>
                <Select
                  value={sevaForm.availability}
                  onChange={(e) => setSevaForm({...sevaForm, availability: e.target.value})}
                  label="Availability"
                >
                  {availabilityOptions.map(opt => (
                    <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Time Slot (e.g., Morning, Evening)"
                value={sevaForm.time_slot}
                onChange={(e) => setSevaForm({...sevaForm, time_slot: e.target.value})}
                fullWidth
              />
            </Grid>

            {/* Day Selection */}
            {sevaForm.availability === 'specific_day' && (
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Specific Day</InputLabel>
                  <Select
                    value={sevaForm.specific_day}
                    onChange={(e) => setSevaForm({...sevaForm, specific_day: e.target.value})}
                    label="Specific Day"
                  >
                    {weekDays.map(day => (
                      <MenuItem key={day.value} value={day.value}>{day.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
            {sevaForm.availability === 'except_day' && (
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Except Day</InputLabel>
                  <Select
                    value={sevaForm.except_day}
                    onChange={(e) => setSevaForm({...sevaForm, except_day: e.target.value})}
                    label="Except Day"
                  >
                    {weekDays.map(day => (
                      <MenuItem key={day.value} value={day.value}>{day.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}

            {/* Booking Settings */}
            <Grid item xs={12} sm={4}>
              <TextField
                label="Max Bookings/Day"
                type="number"
                value={sevaForm.max_bookings_per_day}
                onChange={(e) => setSevaForm({...sevaForm, max_bookings_per_day: parseInt(e.target.value) || ''})}
                fullWidth
                helperText="Leave blank for unlimited"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Advance Booking Days"
                type="number"
                value={sevaForm.advance_booking_days}
                onChange={(e) => setSevaForm({...sevaForm, advance_booking_days: parseInt(e.target.value) || 30})}
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Duration (minutes)"
                type="number"
                value={sevaForm.duration_minutes}
                onChange={(e) => setSevaForm({...sevaForm, duration_minutes: parseInt(e.target.value) || ''})}
                fullWidth
              />
            </Grid>

            {/* Additional Info */}
            <Grid item xs={12}>
              <TextField
                label="Benefits"
                value={sevaForm.benefits}
                onChange={(e) => setSevaForm({...sevaForm, benefits: e.target.value})}
                multiline
                rows={2}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Instructions"
                value={sevaForm.instructions}
                onChange={(e) => setSevaForm({...sevaForm, instructions: e.target.value})}
                multiline
                rows={2}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Materials Required"
                value={sevaForm.materials_required}
                onChange={(e) => setSevaForm({...sevaForm, materials_required: e.target.value})}
                multiline
                rows={3}
                fullWidth
                helperText="Enter materials needed for this seva (comma-separated or one per line). Example: Flowers, Coconut, Camphor, Incense sticks"
                placeholder="e.g., Flowers, Coconut, Camphor, Incense sticks"
              />
            </Grid>

            {/* Toggles */}
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={sevaForm.requires_approval}
                    onChange={(e) => setSevaForm({...sevaForm, requires_approval: e.target.checked})}
                  />
                }
                label="Requires Admin Approval"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={sevaForm.is_active}
                    onChange={(e) => setSevaForm({...sevaForm, is_active: e.target.checked})}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveSevaForm}
            variant="contained"
            disabled={!sevaForm.name_english || !sevaForm.amount}
          >
            {isEditMode ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete <strong>{selectedSeva?.name_english}</strong>?
            This will mark it as inactive and it won't be available for new bookings.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default SevaManagement;
