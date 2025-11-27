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

function DetailedDonationReport() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fromDate, setFromDate] = useState(new Date());
  const [toDate, setToDate] = useState(new Date());
  const [categoryFilter, setCategoryFilter] = useState('');
  const [paymentModeFilter, setPaymentModeFilter] = useState('');
  const [categories, setCategories] = useState([]);
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/v1/donations/categories/');
      setCategories(response.data.map(cat => cat.name));
    } catch (err) {
      console.error('Failed to load categories');
    }
  };

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {
        from_date: fromDate.toISOString().split('T')[0],
        to_date: toDate.toISOString().split('T')[0],
      };
      
      if (categoryFilter) params.category = categoryFilter;
      if (paymentModeFilter) params.payment_mode = paymentModeFilter;
      
      const response = await api.get('/api/v1/reports/donations/detailed', { params });
      
      setReportData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load report');
      console.error('Report error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    if (!reportData) return;

    const exportData = reportData.donations.map(d => ({
      'Date': new Date(d.date).toLocaleDateString(),
      'Receipt Number': d.receipt_number,
      'Devotee Name': d.devotee_name,
      'Mobile': d.devotee_mobile || 'N/A',
      'Category': d.category,
      'Payment Mode': d.payment_mode,
      'Amount (₹)': d.amount,
    }));

    if (format === 'csv') {
      exportToCSV(exportData, `detailed-donation-${fromDate.toISOString().split('T')[0]}`);
    } else if (format === 'excel') {
      exportToExcel(exportData, `Detailed Donation Report`);
    }
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Detailed Donation Report
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
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map(cat => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Payment Mode</InputLabel>
                <Select
                  value={paymentModeFilter}
                  onChange={(e) => setPaymentModeFilter(e.target.value)}
                  label="Payment Mode"
                >
                  <MenuItem value="">All Modes</MenuItem>
                  <MenuItem value="Cash">Cash</MenuItem>
                  <MenuItem value="UPI">UPI</MenuItem>
                  <MenuItem value="Card">Card</MenuItem>
                  <MenuItem value="Online">Online</MenuItem>
                  <MenuItem value="Cheque">Cheque</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={fetchReport}
                disabled={loading}
                sx={{ minWidth: 200 }}
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
                Total: {reportData.total_count} donations | 
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
                    <TableCell><strong>Devotee Name</strong></TableCell>
                    <TableCell><strong>Mobile</strong></TableCell>
                    <TableCell><strong>Category</strong></TableCell>
                    <TableCell><strong>Payment Mode</strong></TableCell>
                    <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.donations.map((donation) => (
                    <TableRow key={donation.id}>
                      <TableCell>{new Date(donation.date).toLocaleDateString()}</TableCell>
                      <TableCell>{donation.receipt_number}</TableCell>
                      <TableCell>{donation.devotee_name}</TableCell>
                      <TableCell>{donation.devotee_mobile || 'N/A'}</TableCell>
                      <TableCell>{donation.category}</TableCell>
                      <TableCell>{donation.payment_mode}</TableCell>
                      <TableCell align="right">
                        {new Intl.NumberFormat('en-IN', {
                          style: 'currency',
                          currency: 'INR',
                          maximumFractionDigits: 0,
                        }).format(donation.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
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
      </Box>
    </Layout>
  );
}

export default DetailedDonationReport;







