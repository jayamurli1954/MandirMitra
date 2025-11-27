import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

function HundiManagement() {
  const { showSuccess, showError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  
  // Data
  const [hundiMasters, setHundiMasters] = useState([]);
  const [hundiOpenings, setHundiOpenings] = useState([]);
  const [selectedOpening, setSelectedOpening] = useState(null);
  
  // Dialogs
  const [masterDialogOpen, setMasterDialogOpen] = useState(false);
  const [openingDialogOpen, setOpeningDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [countingDialogOpen, setCountingDialogOpen] = useState(false);
  
  // Forms
  const [masterForm, setMasterForm] = useState({
    hundi_code: '',
    hundi_name: '',
    hundi_location: '',
    description: '',
    requires_verification: true,
    min_verifiers: 2,
  });
  
  const [openingForm, setOpeningForm] = useState({
    hundi_code: '',
    scheduled_date: new Date().toISOString().split('T')[0],
    scheduled_time: '',
    sealed_number: '',
    notes: '',
  });
  
  const [denominationCounts, setDenominationCounts] = useState([
    { denomination_value: 2000, denomination_type: 'note', quantity: 0 },
    { denomination_value: 500, denomination_type: 'note', quantity: 0 },
    { denomination_value: 100, denomination_type: 'note', quantity: 0 },
    { denomination_value: 50, denomination_type: 'note', quantity: 0 },
    { denomination_value: 20, denomination_type: 'note', quantity: 0 },
    { denomination_value: 10, denomination_type: 'note', quantity: 0 },
    { denomination_value: 5, denomination_type: 'coin', quantity: 0 },
    { denomination_value: 2, denomination_type: 'coin', quantity: 0 },
    { denomination_value: 1, denomination_type: 'coin', quantity: 0 },
  ]);

  useEffect(() => {
    fetchHundiMasters();
    fetchHundiOpenings();
  }, []);

  const fetchHundiMasters = async () => {
    try {
      const response = await api.get('/api/v1/hundi/masters');
      setHundiMasters(response.data);
    } catch (err) {
      console.error('Failed to fetch hundi masters:', err);
    }
  };

  const fetchHundiOpenings = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/hundi/openings?limit=100');
      setHundiOpenings(response.data);
    } catch (err) {
      showError('Failed to fetch hundi openings');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateMaster = async () => {
    try {
      setLoading(true);
      await api.post('/api/v1/hundi/masters', masterForm);
      showSuccess('Hundi master created successfully');
      setMasterDialogOpen(false);
      setMasterForm({
        hundi_code: '',
        hundi_name: '',
        hundi_location: '',
        description: '',
        requires_verification: true,
        min_verifiers: 2,
      });
      fetchHundiMasters();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create hundi master');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOpening = async () => {
    try {
      setLoading(true);
      await api.post('/api/v1/hundi/openings', openingForm);
      showSuccess('Hundi opening scheduled successfully');
      setOpeningDialogOpen(false);
      setOpeningForm({
        hundi_code: '',
        scheduled_date: new Date().toISOString().split('T')[0],
        scheduled_time: '',
        sealed_number: '',
        notes: '',
      });
      fetchHundiOpenings();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to schedule hundi opening');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenHundi = async (openingId) => {
    try {
      setLoading(true);
      await api.post(`/api/v1/hundi/openings/${openingId}/open`);
      showSuccess('Hundi marked as opened');
      fetchHundiOpenings();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to open hundi');
    } finally {
      setLoading(false);
    }
  };

  const handleStartCounting = async (openingId) => {
    try {
      setLoading(true);
      await api.post(`/api/v1/hundi/openings/${openingId}/start-counting`, {});
      showSuccess('Counting started');
      fetchHundiOpenings();
      setCountingDialogOpen(true);
      const response = await api.get(`/api/v1/hundi/openings/${openingId}`);
      setSelectedOpening(response.data);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to start counting');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteCounting = async (openingId) => {
    try {
      setLoading(true);
      const counts = denominationCounts
        .filter(c => c.quantity > 0)
        .map(c => ({
          denomination_value: c.denomination_value,
          denomination_type: c.denomination_type,
          currency: 'INR',
          quantity: c.quantity,
          total_amount: c.denomination_value * c.quantity,
        }));
      
      await api.post(`/api/v1/hundi/openings/${openingId}/complete-counting`, {
        denomination_counts: counts,
      });
      showSuccess('Counting completed successfully');
      setCountingDialogOpen(false);
      fetchHundiOpenings();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to complete counting');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (openingId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/hundi/openings/${openingId}`);
      setSelectedOpening(response.data);
      setDetailsDialogOpen(true);
    } catch (err) {
      showError('Failed to fetch hundi details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      scheduled: 'default',
      opened: 'info',
      counting: 'warning',
      verified: 'success',
      deposited: 'success',
      reconciled: 'success',
      cancelled: 'error',
    };
    return colors[status] || 'default';
  };

  const getStatusSteps = (status) => {
    const steps = ['Scheduled', 'Opened', 'Counting', 'Verified', 'Deposited', 'Reconciled'];
    const statusIndex = {
      scheduled: 0,
      opened: 1,
      counting: 2,
      verified: 3,
      deposited: 4,
      reconciled: 5,
      cancelled: -1,
    };
    return { steps, activeStep: statusIndex[status] || 0 };
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Hundi Management
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {tabValue === 0 && (
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => setMasterDialogOpen(true)}
              >
                Add Hundi Master
              </Button>
            )}
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpeningDialogOpen(true)}
            >
              Schedule Opening
            </Button>
          </Box>
        </Box>

        <Paper sx={{ mb: 3 }}>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Hundi Openings" />
            <Tab label="Hundi Masters" />
          </Tabs>
        </Paper>

        {tabValue === 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Hundi Code</TableCell>
                  <TableCell>Scheduled Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Total Amount</TableCell>
                  <TableCell>Verified</TableCell>
                  <TableCell>Deposited</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : hundiOpenings.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Alert severity="info">No hundi openings found. Schedule your first opening to get started.</Alert>
                    </TableCell>
                  </TableRow>
                ) : (
                  hundiOpenings.map((opening) => {
                    const { steps, activeStep } = getStatusSteps(opening.status);
                    return (
                      <TableRow key={opening.id}>
                        <TableCell>{opening.hundi_code}</TableCell>
                        <TableCell>{new Date(opening.scheduled_date).toLocaleDateString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={opening.status}
                            color={getStatusColor(opening.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>₹{opening.total_amount?.toLocaleString() || '0'}</TableCell>
                        <TableCell>
                          {opening.verified ? (
                            <CheckCircleIcon color="success" fontSize="small" />
                          ) : (
                            <Chip label="Pending" size="small" color="warning" />
                          )}
                        </TableCell>
                        <TableCell>
                          {opening.deposited ? (
                            <AccountBalanceIcon color="success" fontSize="small" />
                          ) : (
                            <Chip label="Pending" size="small" color="warning" />
                          )}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            color="info"
                            onClick={() => handleViewDetails(opening.id)}
                          >
                            <VisibilityIcon />
                          </IconButton>
                          {opening.status === 'scheduled' && (
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleOpenHundi(opening.id)}
                            >
                              <PlayArrowIcon />
                            </IconButton>
                          )}
                          {opening.status === 'opened' && (
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleStartCounting(opening.id)}
                            >
                              <PlayArrowIcon />
                            </IconButton>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {tabValue === 1 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Hundi Code</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Verification Required</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {hundiMasters.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Alert severity="info">No hundi masters found. Add your first hundi master.</Alert>
                    </TableCell>
                  </TableRow>
                ) : (
                  hundiMasters.map((master) => (
                    <TableRow key={master.id}>
                      <TableCell>{master.hundi_code}</TableCell>
                      <TableCell>{master.hundi_name}</TableCell>
                      <TableCell>{master.hundi_location || 'N/A'}</TableCell>
                      <TableCell>
                        {master.requires_verification ? `Yes (${master.min_verifiers} persons)` : 'No'}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={master.is_active ? 'Active' : 'Inactive'}
                          color={master.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Hundi Master Dialog */}
        <Dialog open={masterDialogOpen} onClose={() => setMasterDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Hundi Master</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Hundi Code"
                  value={masterForm.hundi_code}
                  onChange={(e) => setMasterForm({ ...masterForm, hundi_code: e.target.value.toUpperCase() })}
                  required
                  helperText="Unique code (e.g., HUNDI-001, MAIN-HUNDI)"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Hundi Name"
                  value={masterForm.hundi_name}
                  onChange={(e) => setMasterForm({ ...masterForm, hundi_name: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Location"
                  value={masterForm.hundi_location}
                  onChange={(e) => setMasterForm({ ...masterForm, hundi_location: e.target.value })}
                  helperText="Physical location of the hundi"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={masterForm.description}
                  onChange={(e) => setMasterForm({ ...masterForm, description: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setMasterDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleCreateMaster}
              disabled={loading || !masterForm.hundi_code || !masterForm.hundi_name}
            >
              {loading ? <CircularProgress size={20} /> : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Schedule Opening Dialog */}
        <Dialog open={openingDialogOpen} onClose={() => setOpeningDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Schedule Hundi Opening</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Hundi</InputLabel>
                  <Select
                    value={openingForm.hundi_code}
                    onChange={(e) => setOpeningForm({ ...openingForm, hundi_code: e.target.value })}
                    label="Hundi"
                    required
                  >
                    {hundiMasters.filter(m => m.is_active).map((master) => (
                      <MenuItem key={master.id} value={master.hundi_code}>
                        {master.hundi_code} - {master.hundi_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Scheduled Date"
                  type="date"
                  value={openingForm.scheduled_date}
                  onChange={(e) => setOpeningForm({ ...openingForm, scheduled_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Scheduled Time"
                  type="time"
                  value={openingForm.scheduled_time}
                  onChange={(e) => setOpeningForm({ ...openingForm, scheduled_time: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Sealed Number"
                  value={openingForm.sealed_number}
                  onChange={(e) => setOpeningForm({ ...openingForm, sealed_number: e.target.value })}
                  helperText="Sealed number on the hundi"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  value={openingForm.notes}
                  onChange={(e) => setOpeningForm({ ...openingForm, notes: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpeningDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleCreateOpening}
              disabled={loading || !openingForm.hundi_code}
            >
              {loading ? <CircularProgress size={20} /> : 'Schedule'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Counting Dialog */}
        <Dialog open={countingDialogOpen} onClose={() => setCountingDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Count Hundi - Denomination Wise</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {denominationCounts.map((count, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">₹{count.denomination_value} ({count.denomination_type})</Typography>
                      <TextField
                        fullWidth
                        type="number"
                        label="Quantity"
                        value={count.quantity}
                        onChange={(e) => {
                          const newCounts = [...denominationCounts];
                          newCounts[index].quantity = parseInt(e.target.value) || 0;
                          setDenominationCounts(newCounts);
                        }}
                        inputProps={{ min: 0 }}
                      />
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        Total: ₹{(count.denomination_value * count.quantity).toLocaleString()}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Total Amount</Typography>
                    <Typography variant="h4" color="primary">
                      ₹{denominationCounts.reduce((sum, c) => sum + (c.denomination_value * c.quantity), 0).toLocaleString()}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCountingDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={() => handleCompleteCounting(selectedOpening?.id)}
              disabled={loading || denominationCounts.every(c => c.quantity === 0)}
            >
              {loading ? <CircularProgress size={20} /> : 'Complete Counting'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Details Dialog */}
        <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Hundi Opening Details</DialogTitle>
          <DialogContent>
            {selectedOpening && (
              <Box sx={{ mt: 2 }}>
                <Stepper activeStep={getStatusSteps(selectedOpening.status).activeStep} alternativeLabel>
                  {getStatusSteps(selectedOpening.status).steps.map((label) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
                
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Hundi Code</Typography>
                    <Typography variant="body1">{selectedOpening.hundi_code}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Status</Typography>
                    <Chip label={selectedOpening.status} color={getStatusColor(selectedOpening.status)} />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Total Amount</Typography>
                    <Typography variant="h6">₹{selectedOpening.total_amount?.toLocaleString() || '0'}</Typography>
                  </Grid>
                  {selectedOpening.denomination_counts && selectedOpening.denomination_counts.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="h6" sx={{ mb: 2 }}>Denomination Breakdown</Typography>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Denomination</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Amount</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {selectedOpening.denomination_counts.map((count, idx) => (
                            <TableRow key={idx}>
                              <TableCell>₹{count.denomination_value}</TableCell>
                              <TableCell>{count.denomination_type}</TableCell>
                              <TableCell>{count.quantity}</TableCell>
                              <TableCell>₹{count.total_amount.toLocaleString()}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default HundiManagement;

