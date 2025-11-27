import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
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
  TextField,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import Layout from '../components/Layout';
import api from '../services/api';
import ExportButton from '../components/ExportButton';
import PrintButton from '../components/PrintButton';
import { exportToCSV, exportToExcel } from '../utils/export';
import { useNotification } from '../contexts/NotificationContext';

function SevaSchedule() {
  const { showSuccess, showError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [days, setDays] = useState(3);
  const [scheduleData, setScheduleData] = useState(null);
  const [priests, setPriests] = useState([]);
  const [priestDialog, setPriestDialog] = useState({ open: false, booking: null });
  const [selectedPriestId, setSelectedPriestId] = useState('');
  const [refundDialog, setRefundDialog] = useState({ open: false, booking: null });
  const [refundForm, setRefundForm] = useState({
    refund_amount: '',
    refund_method: 'original',
    refund_reference: '',
  });

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await api.get('/api/v1/reports/sevas/schedule', {
        params: { days }
      });
      
      setScheduleData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load schedule');
      console.error('Schedule error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedule();
    fetchPriests();
  }, [days]);

  const fetchPriests = async () => {
    try {
      const response = await api.get('/api/v1/sevas/priests');
      setPriests(response.data);
    } catch (err) {
      console.error('Failed to fetch priests:', err);
    }
  };

  const handleAssignPriest = (booking) => {
    setPriestDialog({ open: true, booking });
    setSelectedPriestId(booking.priest_id || '');
  };

  const handleConfirmPriestAssignment = async () => {
    try {
      if (selectedPriestId) {
        await api.put(`/api/v1/sevas/bookings/${priestDialog.booking.id}/assign-priest`, null, {
          params: { priest_id: selectedPriestId }
        });
        showSuccess('Priest assigned successfully');
      } else {
        await api.put(`/api/v1/sevas/bookings/${priestDialog.booking.id}/remove-priest`);
        showSuccess('Priest assignment removed');
      }
      setPriestDialog({ open: false, booking: null });
      fetchSchedule();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to assign priest');
    }
  };

  const handleProcessRefund = (booking) => {
    const expectedRefund = booking.amount_paid * 0.9;
    setRefundForm({
      refund_amount: expectedRefund.toFixed(2),
      refund_method: 'original',
      refund_reference: '',
    });
    setRefundDialog({ open: true, booking });
  };

  const handleConfirmRefund = async () => {
    try {
      await api.post(`/api/v1/sevas/bookings/${refundDialog.booking.id}/process-refund`, null, {
        params: {
          refund_amount: refundForm.refund_amount,
          refund_method: refundForm.refund_method,
          refund_reference: refundForm.refund_reference,
        }
      });
      showSuccess('Refund processed successfully');
      setRefundDialog({ open: false, booking: null });
      fetchSchedule();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to process refund');
    }
  };

  const handleExport = (format) => {
    if (!scheduleData) return;

    const exportData = scheduleData.schedule.map(s => ({
      'Date': new Date(s.date).toLocaleDateString(),
      'Time': s.time || 'N/A',
      'Seva Name': s.seva_name,
      'Devotee Name': s.devotee_name,
      'Mobile': s.devotee_mobile || 'N/A',
      'Amount (₹)': s.amount,
      'Status': s.status,
      'Special Request': s.special_request || 'N/A',
    }));

    if (format === 'csv') {
      exportToCSV(exportData, `seva-schedule-${days}-days`);
    } else if (format === 'excel') {
      exportToExcel(exportData, `Seva Schedule - Next ${days} Days`);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'Today') return 'primary';
    if (status === 'Completed') return 'success';
    if (status === 'Upcoming') return 'warning';
    return 'default';
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Seva Schedule - Next {days} Days
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Days Selector */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                label="Number of Days"
                type="number"
                value={days}
                onChange={(e) => setDays(parseInt(e.target.value) || 3)}
                inputProps={{ min: 1, max: 30 }}
                size="small"
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button
                variant="contained"
                onClick={fetchSchedule}
                disabled={loading}
                fullWidth
              >
                {loading ? <CircularProgress size={20} /> : 'Refresh Schedule'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Schedule Table */}
        {scheduleData && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Period: {new Date(scheduleData.from_date).toLocaleDateString()} to {new Date(scheduleData.to_date).toLocaleDateString()} | 
                Total Bookings: {scheduleData.total_bookings}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <ExportButton onExport={handleExport} />
                <PrintButton />
              </Box>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Date</strong></TableCell>
                    <TableCell><strong>Time</strong></TableCell>
                    <TableCell><strong>Seva Name</strong></TableCell>
                    <TableCell><strong>Devotee Name</strong></TableCell>
                    <TableCell><strong>Mobile</strong></TableCell>
                    <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell><strong>Priest</strong></TableCell>
                    <TableCell><strong>Special Request</strong></TableCell>
                    <TableCell><strong>Actions</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {scheduleData.schedule.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={10} align="center">
                        <Typography color="text.secondary">No sevas scheduled for the next {days} days</Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    scheduleData.schedule.map((item) => (
                      <TableRow key={item.id}>
                        <TableCell>{new Date(item.date).toLocaleDateString()}</TableCell>
                        <TableCell>{item.time || 'N/A'}</TableCell>
                        <TableCell>{item.seva_name}</TableCell>
                        <TableCell>{item.devotee_name}</TableCell>
                        <TableCell>{item.devotee_mobile || 'N/A'}</TableCell>
                        <TableCell align="right">
                          {new Intl.NumberFormat('en-IN', {
                            style: 'currency',
                            currency: 'INR',
                            maximumFractionDigits: 0,
                          }).format(item.amount)}
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={item.status} 
                            color={getStatusColor(item.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{item.priest?.name || 'Not Assigned'}</TableCell>
                        <TableCell>{item.special_request || 'N/A'}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleAssignPriest(item)}
                              title="Assign Priest"
                            >
                              <PersonAddIcon fontSize="small" />
                            </IconButton>
                            {item.status === 'Cancelled' && (
                              <IconButton
                                size="small"
                                color="secondary"
                                onClick={() => handleProcessRefund(item)}
                                title="Process Refund"
                              >
                                <AccountBalanceIcon fontSize="small" />
                              </IconButton>
                            )}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Priest Assignment Dialog */}
        <Dialog open={priestDialog.open} onClose={() => setPriestDialog({ open: false, booking: null })} maxWidth="sm" fullWidth>
          <DialogTitle>Assign Priest</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Select Priest</InputLabel>
                <Select
                  value={selectedPriestId}
                  onChange={(e) => setSelectedPriestId(e.target.value)}
                  label="Select Priest"
                >
                  <MenuItem value="">None (Remove Assignment)</MenuItem>
                  {priests.map((priest) => (
                    <MenuItem key={priest.id} value={priest.id}>
                      {priest.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              {priestDialog.booking && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Seva: {priestDialog.booking.seva_name}<br />
                  Devotee: {priestDialog.booking.devotee_name}<br />
                  Date: {new Date(priestDialog.booking.date).toLocaleDateString()}
                </Typography>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setPriestDialog({ open: false, booking: null })}>Cancel</Button>
            <Button variant="contained" onClick={handleConfirmPriestAssignment}>
              {selectedPriestId ? 'Assign' : 'Remove Assignment'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Refund Processing Dialog */}
        <Dialog open={refundDialog.open} onClose={() => setRefundDialog({ open: false, booking: null })} maxWidth="sm" fullWidth>
          <DialogTitle>Process Refund</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              {refundDialog.booking && (
                <>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Booking Amount: ₹{refundDialog.booking.amount_paid.toLocaleString()}<br />
                    Processing Fee (10%): ₹{(refundDialog.booking.amount_paid * 0.1).toFixed(2)}<br />
                    Refund Amount (90%): ₹{(refundDialog.booking.amount_paid * 0.9).toFixed(2)}
                  </Alert>
                  <TextField
                    fullWidth
                    label="Refund Amount"
                    type="number"
                    value={refundForm.refund_amount}
                    onChange={(e) => setRefundForm({ ...refundForm, refund_amount: e.target.value })}
                    sx={{ mb: 2 }}
                    helperText="Default: 90% of booking amount"
                  />
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Refund Method</InputLabel>
                    <Select
                      value={refundForm.refund_method}
                      onChange={(e) => setRefundForm({ ...refundForm, refund_method: e.target.value })}
                      label="Refund Method"
                    >
                      <MenuItem value="original">Original Payment Method</MenuItem>
                      <MenuItem value="cash">Cash</MenuItem>
                      <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                    </Select>
                  </FormControl>
                  <TextField
                    fullWidth
                    label="Refund Reference"
                    value={refundForm.refund_reference}
                    onChange={(e) => setRefundForm({ ...refundForm, refund_reference: e.target.value })}
                    helperText="Transaction reference number (optional)"
                  />
                </>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRefundDialog({ open: false, booking: null })}>Cancel</Button>
            <Button variant="contained" color="secondary" onClick={handleConfirmRefund}>
              Process Refund
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default SevaSchedule;







