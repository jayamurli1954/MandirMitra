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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import PostAddIcon from '@mui/icons-material/PostAdd';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

const DepreciationPage = () => {
  const [assets, setAssets] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [calculateDialogOpen, setCalculateDialogOpen] = useState(false);
  const [postDialogOpen, setPostDialogOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [selectedSchedule, setSelectedSchedule] = useState(null);

  const [calculateForm, setCalculateForm] = useState({
    asset_id: '',
    financial_year: `${new Date().getFullYear()}-${String(new Date().getFullYear() + 1).slice(-2)}`,
    period: 'yearly',
    period_start_date: new Date(new Date().getFullYear(), 3, 1), // April 1
    period_end_date: new Date(new Date().getFullYear() + 1, 2, 31), // March 31
    units_produced_this_period: '',
    interest_rate_override: '',
  });

  const [postForm, setPostForm] = useState({
    schedule_id: '',
    post_date: new Date(),
  });

  useEffect(() => {
    fetchAssets();
    fetchSchedules();
  }, []);

  const fetchAssets = async () => {
    try {
      const response = await api.get('/api/v1/assets/');
      setAssets(response.data.filter(a => a.is_depreciable && a.status === 'active'));
    } catch (err) {
      setError('Failed to load assets');
    }
  };

  const fetchSchedules = async (assetId = null) => {
    if (!assetId && !selectedAsset) {
      setSchedules([]);
      return;
    }
    try {
      setLoading(true);
      const id = assetId || selectedAsset?.id;
      if (id) {
        const response = await api.get(`/api/v1/assets/depreciation/schedule/${id}`);
        setSchedules(response.data || []);
      }
    } catch (err) {
      console.error('Error fetching schedules:', err);
      setSchedules([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const requestData = {
        ...calculateForm,
        asset_id: parseInt(calculateForm.asset_id),
        period_start_date: calculateForm.period_start_date.toISOString().split('T')[0],
        period_end_date: calculateForm.period_end_date.toISOString().split('T')[0],
        units_produced_this_period: calculateForm.units_produced_this_period ? parseFloat(calculateForm.units_produced_this_period) : null,
        interest_rate_override: calculateForm.interest_rate_override ? parseFloat(calculateForm.interest_rate_override) : null,
      };

      await api.post('/api/v1/assets/depreciation/calculate/', requestData);
      setSuccess('Depreciation calculated successfully');
      setCalculateDialogOpen(false);
      fetchSchedules();
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to calculate depreciation');
    }
  };

  const handlePost = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const requestData = {
        schedule_id: parseInt(postForm.schedule_id),
        post_date: postForm.post_date.toISOString().split('T')[0],
      };

      await api.post('/api/v1/assets/depreciation/post/', requestData);
      setSuccess('Depreciation posted to accounting successfully');
      setPostDialogOpen(false);
      fetchSchedules();
      fetchAssets();
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post depreciation');
    }
  };

  const handleBatchCalculate = async () => {
    if (!window.confirm('Calculate depreciation for all active assets?')) return;

    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await api.post('/api/v1/assets/depreciation/calculate-batch/', null, {
        params: {
          financial_year: calculateForm.financial_year,
          period: calculateForm.period,
          period_start_date: calculateForm.period_start_date.toISOString().split('T')[0],
          period_end_date: calculateForm.period_end_date.toISOString().split('T')[0],
        }
      });
      setSuccess(`Depreciation calculated for ${response.data.successful} assets`);
      fetchSchedules();
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to calculate batch depreciation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Depreciation Management
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<CalculateIcon />}
              onClick={() => {
                setSelectedAsset(null);
                setCalculateForm({
                  asset_id: '',
                  financial_year: `${new Date().getFullYear()}-${String(new Date().getFullYear() + 1).slice(-2)}`,
                  period: 'yearly',
                  period_start_date: new Date(new Date().getFullYear(), 3, 1),
                  period_end_date: new Date(new Date().getFullYear() + 1, 2, 31),
                  units_produced_this_period: '',
                  interest_rate_override: '',
                });
                setCalculateDialogOpen(true);
              }}
            >
              Calculate
            </Button>
            <Button
              variant="outlined"
              onClick={handleBatchCalculate}
              disabled={loading}
            >
              Batch Calculate
            </Button>
          </Box>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>Depreciation Schedules</Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Asset</TableCell>
                    <TableCell>Financial Year</TableCell>
                    <TableCell>Period</TableCell>
                    <TableCell>Opening Value</TableCell>
                    <TableCell>Depreciation</TableCell>
                    <TableCell>Closing Value</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {schedules.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                        <Typography variant="body2" color="text.secondary">
                          No depreciation schedules found. Calculate depreciation to see schedules.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    schedules.map((schedule) => (
                      <TableRow key={schedule.id}>
                        <TableCell>{schedule.asset?.name || 'N/A'}</TableCell>
                        <TableCell>{schedule.financial_year}</TableCell>
                        <TableCell>{schedule.period}</TableCell>
                        <TableCell>₹{schedule.opening_book_value?.toLocaleString() || 0}</TableCell>
                        <TableCell>₹{schedule.depreciation_amount?.toLocaleString() || 0}</TableCell>
                        <TableCell>₹{schedule.closing_book_value?.toLocaleString() || 0}</TableCell>
                        <TableCell>
                          <Chip
                            label={schedule.status}
                            size="small"
                            color={schedule.status === 'posted' ? 'success' : 'warning'}
                          />
                        </TableCell>
                        <TableCell>
                          {schedule.status === 'calculated' && (
                            <Button
                              size="small"
                              variant="outlined"
                              startIcon={<PostAddIcon />}
                              onClick={() => {
                                setSelectedSchedule(schedule);
                                setPostForm({
                                  schedule_id: schedule.id,
                                  post_date: new Date(),
                                });
                                setPostDialogOpen(true);
                              }}
                            >
                              Post
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>

        {/* Calculate Dialog */}
        <Dialog open={calculateDialogOpen} onClose={() => setCalculateDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handleCalculate}>
            <DialogTitle>Calculate Depreciation</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    select
                    label="Asset *"
                    value={calculateForm.asset_id}
                    onChange={(e) => setCalculateForm({ ...calculateForm, asset_id: e.target.value })}
                    required
                  >
                    {assets.map((asset) => (
                      <MenuItem key={asset.id} value={asset.id}>
                        {asset.asset_number} - {asset.name}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Financial Year *"
                    value={calculateForm.financial_year}
                    onChange={(e) => setCalculateForm({ ...calculateForm, financial_year: e.target.value })}
                    required
                    placeholder="2024-25"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Period *"
                    value={calculateForm.period}
                    onChange={(e) => setCalculateForm({ ...calculateForm, period: e.target.value })}
                    required
                  >
                    <MenuItem value="monthly">Monthly</MenuItem>
                    <MenuItem value="yearly">Yearly</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Period Start Date *"
                      value={calculateForm.period_start_date}
                      onChange={(newValue) => setCalculateForm({ ...calculateForm, period_start_date: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth required />}
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Period End Date *"
                      value={calculateForm.period_end_date}
                      onChange={(newValue) => setCalculateForm({ ...calculateForm, period_end_date: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth required />}
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Units Produced (for Units of Production)"
                    value={calculateForm.units_produced_this_period}
                    onChange={(e) => setCalculateForm({ ...calculateForm, units_produced_this_period: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Interest Rate % (for Annuity/Sinking Fund)"
                    value={calculateForm.interest_rate_override}
                    onChange={(e) => setCalculateForm({ ...calculateForm, interest_rate_override: e.target.value })}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setCalculateDialogOpen(false)}>Cancel</Button>
              <Button type="submit" variant="contained">Calculate</Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Post Dialog */}
        <Dialog open={postDialogOpen} onClose={() => setPostDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handlePost}>
            <DialogTitle>Post Depreciation to Accounting</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Schedule ID"
                    value={postForm.schedule_id}
                    disabled
                  />
                </Grid>
                <Grid item xs={12}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Post Date *"
                      value={postForm.post_date}
                      onChange={(newValue) => setPostForm({ ...postForm, post_date: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth required />}
                    />
                  </LocalizationProvider>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setPostDialogOpen(false)}>Cancel</Button>
              <Button type="submit" variant="contained">Post to Accounting</Button>
            </DialogActions>
          </form>
        </Dialog>
      </Container>
    </Layout>
  );
};

export default DepreciationPage;

