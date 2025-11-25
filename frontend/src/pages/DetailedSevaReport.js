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
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import Layout from '../components/Layout';
import api from '../services/api';
import ExportButton from '../components/ExportButton';
import PrintButton from '../components/PrintButton';
import { exportToCSV, exportToExcel } from '../utils/export';
import { useNotification } from '../contexts/NotificationContext';

function DetailedSevaReport() {
  const { showSuccess, showError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fromDate, setFromDate] = useState(new Date());
  const [toDate, setToDate] = useState(new Date());
  const [statusFilter, setStatusFilter] = useState('');
  const [reportData, setReportData] = useState(null);
  const [rescheduleDialog, setRescheduleDialog] = useState({ open: false, booking: null });
  const [newDate, setNewDate] = useState(null);
  const [rescheduleReason, setRescheduleReason] = useState('');

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {
        from_date: fromDate.toISOString().split('T')[0],
        to_date: toDate.toISOString().split('T')[0],
      };
      
      if (statusFilter) params.status = statusFilter;
      
      const response = await api.get('/api/v1/reports/sevas/detailed', { params });
      
      setReportData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load report');
      console.error('Report error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handleReschedule = (booking) => {
    setRescheduleDialog({ open: true, booking });
    setNewDate(new Date(booking.seva_date));
    setRescheduleReason('');
  };

  const submitReschedule = async () => {
    try {
      await api.put(`/api/v1/sevas/bookings/${rescheduleDialog.booking.id}/reschedule`, null, {
        params: {
          new_date: newDate.toISOString().split('T')[0],
          reason: rescheduleReason,
        }
      });
      
      showSuccess('Reschedule request submitted. Waiting for admin approval.');
      setRescheduleDialog({ open: false, booking: null });
      fetchReport();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to submit reschedule request');
    }
  };

  const handleExport = (format) => {
    if (!reportData) return;

    const exportData = reportData.sevas.map(s => ({
      'Date': new Date(s.seva_date).toLocaleDateString(),
      'Receipt Number': s.receipt_number,
      'Seva Name': s.seva_name,
      'Devotee Name': s.devotee_name,
      'Mobile': s.devotee_mobile || 'N/A',
      'Amount (₹)': s.amount,
      'Status': s.status,
    }));

    if (format === 'csv') {
      exportToCSV(exportData, `detailed-seva-${fromDate.toISOString().split('T')[0]}`);
    } else if (format === 'excel') {
      exportToExcel(exportData, `Detailed Seva Report`);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'Completed') return 'success';
    if (status === 'Pending') return 'warning';
    return 'default';
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Detailed Seva Report
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="From Date"
                  value={fromDate}
                  onChange={(newValue) => setFromDate(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} sm={3}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="To Date"
                  value={toDate}
                  onChange={(newValue) => setToDate(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant="contained"
                fullWidth
                onClick={fetchReport}
                disabled={loading}
                sx={{ height: '40px' }}
              >
                {loading ? <CircularProgress size={20} /> : 'Generate Report'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Report Table */}
        {reportData && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Total: {reportData.total_count} sevas | 
                Completed: {reportData.completed_count} | 
                Pending: {reportData.pending_count} | 
                Amount: ₹{new Intl.NumberFormat('en-IN').format(reportData.total_amount)}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <ExportButton onExport={handleExport} />
                <PrintButton />
              </Box>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Date</strong></TableCell>
                    <TableCell><strong>Receipt #</strong></TableCell>
                    <TableCell><strong>Seva Name</strong></TableCell>
                    <TableCell><strong>Devotee Name</strong></TableCell>
                    <TableCell><strong>Mobile</strong></TableCell>
                    <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Action</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.sevas.map((seva) => (
                    <TableRow key={seva.id}>
                      <TableCell>{new Date(seva.seva_date).toLocaleDateString()}</TableCell>
                      <TableCell>{seva.receipt_number}</TableCell>
                      <TableCell>{seva.seva_name}</TableCell>
                      <TableCell>{seva.devotee_name}</TableCell>
                      <TableCell>{seva.devotee_mobile || 'N/A'}</TableCell>
                      <TableCell align="right">
                        {new Intl.NumberFormat('en-IN', {
                          style: 'currency',
                          currency: 'INR',
                          maximumFractionDigits: 0,
                        }).format(seva.amount)}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={seva.status} 
                          color={getStatusColor(seva.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {seva.status === 'Pending' && (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleReschedule(seva)}
                          >
                            Reschedule
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}

        {/* Reschedule Dialog */}
        <Dialog open={rescheduleDialog.open} onClose={() => setRescheduleDialog({ open: false, booking: null })}>
          <DialogTitle>Reschedule Seva</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Current Date: {rescheduleDialog.booking && new Date(rescheduleDialog.booking.seva_date).toLocaleDateString()}
              </Typography>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="New Date"
                  value={newDate}
                  onChange={(newValue) => setNewDate(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth sx={{ mb: 2 }} />}
                />
              </LocalizationProvider>
              <TextField
                fullWidth
                label="Reason for Reschedule"
                multiline
                rows={3}
                value={rescheduleReason}
                onChange={(e) => setRescheduleReason(e.target.value)}
                required
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRescheduleDialog({ open: false, booking: null })}>Cancel</Button>
            <Button 
              variant="contained" 
              onClick={submitReschedule}
              disabled={!newDate || !rescheduleReason}
            >
              Submit Request
            </Button>
          </DialogActions>
        </Dialog>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}
      </Box>
    </Layout>
  );
}

export default DetailedSevaReport;



