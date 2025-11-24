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
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import Layout from '../components/Layout';
import api from '../services/api';
import ExportButton from '../components/ExportButton';
import PrintButton from '../components/PrintButton';
import { exportToCSV, exportToExcel } from '../utils/export';

function CategoryWiseDonationReport() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fromDate, setFromDate] = useState(new Date());
  const [toDate, setToDate] = useState(new Date());
  const [reportData, setReportData] = useState(null);

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await api.get('/api/v1/reports/donations/category-wise', {
        params: {
          from_date: fromDate.toISOString().split('T')[0],
          to_date: toDate.toISOString().split('T')[0],
        }
      });
      
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

  const handleExport = (format) => {
    if (!reportData) return;

    const exportData = reportData.categories.map(cat => ({
      'Category': cat.category,
      'Count': cat.count,
      'Amount (₹)': cat.amount,
    }));

    if (format === 'csv') {
      exportToCSV(exportData, `category-wise-donation-${fromDate.toISOString().split('T')[0]}`);
    } else if (format === 'excel') {
      exportToExcel(exportData, `Category-Wise Donation Report`);
    }
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Category-Wise Donation Report
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Date Range Selection */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="From Date"
                  value={fromDate}
                  onChange={(newValue) => setFromDate(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} sm={4}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DatePicker
                  label="To Date"
                  value={toDate}
                  onChange={(newValue) => setToDate(newValue)}
                  renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12} sm={4}>
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
                Report Period: {new Date(reportData.from_date).toLocaleDateString()} to {new Date(reportData.to_date).toLocaleDateString()}
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
                    <TableCell><strong>Category</strong></TableCell>
                    <TableCell align="right"><strong>Count</strong></TableCell>
                    <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.categories.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>{item.category}</TableCell>
                      <TableCell align="right">{item.count}</TableCell>
                      <TableCell align="right">
                        {new Intl.NumberFormat('en-IN', {
                          style: 'currency',
                          currency: 'INR',
                          maximumFractionDigits: 0,
                        }).format(item.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow sx={{ backgroundColor: '#f5f5f5', fontWeight: 'bold' }}>
                    <TableCell><strong>TOTAL</strong></TableCell>
                    <TableCell align="right"><strong>{reportData.total_count}</strong></TableCell>
                    <TableCell align="right">
                      <strong>
                        {new Intl.NumberFormat('en-IN', {
                          style: 'currency',
                          currency: 'INR',
                          maximumFractionDigits: 0,
                        }).format(reportData.total_amount)}
                      </strong>
                    </TableCell>
                  </TableRow>
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

export default CategoryWiseDonationReport;

