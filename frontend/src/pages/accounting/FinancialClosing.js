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
  Divider,
} from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

function FinancialClosing() {
  const { showSuccess, showError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  
  // Data
  const [financialYears, setFinancialYears] = useState([]);
  const [activeYear, setActiveYear] = useState(null);
  const [periodClosings, setPeriodClosings] = useState([]);
  const [closingSummary, setClosingSummary] = useState(null);
  
  // Dialogs
  const [yearDialogOpen, setYearDialogOpen] = useState(false);
  const [monthCloseDialogOpen, setMonthCloseDialogOpen] = useState(false);
  const [yearCloseDialogOpen, setYearCloseDialogOpen] = useState(false);
  const [summaryDialogOpen, setSummaryDialogOpen] = useState(false);
  
  // Forms
  const [yearForm, setYearForm] = useState({
    year_code: '',
    start_date: '',
    end_date: '',
  });
  
  const [monthCloseForm, setMonthCloseForm] = useState({
    financial_year_id: '',
    closing_date: new Date().toISOString().split('T')[0],
  });
  
  const [yearCloseForm, setYearCloseForm] = useState({
    financial_year_id: '',
    closing_date: '',
  });

  useEffect(() => {
    fetchFinancialYears();
    fetchActiveYear();
  }, []);

  useEffect(() => {
    if (activeYear) {
      fetchPeriodClosings(activeYear.id);
      setMonthCloseForm(prev => ({ ...prev, financial_year_id: activeYear.id }));
      setYearCloseForm(prev => ({ ...prev, financial_year_id: activeYear.id }));
    }
  }, [activeYear]);

  const fetchFinancialYears = async () => {
    try {
      const response = await api.get('/api/v1/financial-closing/financial-years');
      setFinancialYears(response.data);
    } catch (err) {
      showError('Failed to fetch financial years');
    }
  };

  const fetchActiveYear = async () => {
    try {
      const response = await api.get('/api/v1/financial-closing/financial-years/active');
      setActiveYear(response.data);
    } catch (err) {
      console.log('No active financial year found');
    }
  };

  const fetchPeriodClosings = async (yearId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/financial-closing/period-closings?financial_year_id=${yearId}`);
      setPeriodClosings(response.data);
    } catch (err) {
      showError('Failed to fetch period closings');
    } finally {
      setLoading(false);
    }
  };

  const fetchClosingSummary = async (closingId) => {
    try {
      const response = await api.get(`/api/v1/financial-closing/closings/${closingId}/summary`);
      setClosingSummary(response.data);
      setSummaryDialogOpen(true);
    } catch (err) {
      showError('Failed to fetch closing summary');
    }
  };

  const handleCreateYear = async () => {
    if (!yearForm.year_code || !yearForm.start_date || !yearForm.end_date) {
      showError('Please fill all fields');
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/v1/financial-closing/financial-years', yearForm);
      showSuccess('Financial year created successfully');
      setYearDialogOpen(false);
      setYearForm({
        year_code: '',
        start_date: '',
        end_date: '',
      });
      fetchFinancialYears();
      fetchActiveYear();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create financial year');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseMonth = async () => {
    if (!monthCloseForm.financial_year_id || !monthCloseForm.closing_date) {
      showError('Please select financial year and closing date');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/api/v1/financial-closing/close-month', monthCloseForm);
      showSuccess('Month closed successfully');
      setMonthCloseDialogOpen(false);
      if (activeYear) {
        fetchPeriodClosings(activeYear.id);
      }
      fetchClosingSummary(response.data.id);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to close month');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseYear = async () => {
    if (!yearCloseForm.financial_year_id || !yearCloseForm.closing_date) {
      showError('Please select financial year and closing date');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/api/v1/financial-closing/close-year', yearCloseForm);
      showSuccess('Financial year closed successfully');
      setYearCloseDialogOpen(false);
      fetchFinancialYears();
      fetchActiveYear();
      fetchClosingSummary(response.data.id);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to close financial year');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'success',
      closed: 'default',
      locked: 'warning',
    };
    return colors[status] || 'default';
  };

  const getClosingTypeColor = (type) => {
    return type === 'month_end' ? 'info' : 'primary';
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Financial Closing
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              startIcon={<CalendarMonthIcon />}
              onClick={() => setYearDialogOpen(true)}
            >
              Create Financial Year
            </Button>
            {activeYear && (
              <>
                <Button
                  variant="contained"
                  color="info"
                  onClick={() => setMonthCloseDialogOpen(true)}
                  disabled={activeYear.is_closed}
                >
                  Close Month
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => setYearCloseDialogOpen(true)}
                  disabled={activeYear.is_closed}
                >
                  Close Year
                </Button>
              </>
            )}
          </Box>
        </Box>

        {activeYear && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Active Financial Year</Typography>
                  <Typography variant="h6">{activeYear.year_code}</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Period</Typography>
                  <Typography variant="body1">
                    {new Date(activeYear.start_date).toLocaleDateString()} - {new Date(activeYear.end_date).toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip
                    label={activeYear.is_closed ? 'Closed' : 'Open'}
                    color={activeYear.is_closed ? 'default' : 'success'}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary">Is Active</Typography>
                  <Chip
                    label={activeYear.is_active ? 'Yes' : 'No'}
                    color={activeYear.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        <Paper>
          <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
            <Tab label="Financial Years" />
            <Tab label="Period Closings" />
          </Tabs>

          {tabValue === 0 && (
            <Box sx={{ p: 3 }}>
              {loading ? (
                <CircularProgress />
              ) : financialYears.length === 0 ? (
                <Alert severity="info">No financial years found. Create your first financial year to get started.</Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Year Code</TableCell>
                        <TableCell>Start Date</TableCell>
                        <TableCell>End Date</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Is Active</TableCell>
                        <TableCell>Is Closed</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {financialYears.map((year) => (
                        <TableRow key={year.id}>
                          <TableCell>{year.year_code}</TableCell>
                          <TableCell>{new Date(year.start_date).toLocaleDateString()}</TableCell>
                          <TableCell>{new Date(year.end_date).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={year.is_closed ? 'Closed' : 'Open'}
                              color={getStatusColor(year.is_closed ? 'closed' : 'open')}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={year.is_active ? 'Yes' : 'No'}
                              color={year.is_active ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {year.is_closed ? (
                              <CheckCircleIcon color="success" />
                            ) : (
                              <LockIcon color="disabled" />
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {tabValue === 1 && (
            <Box sx={{ p: 3 }}>
              {loading ? (
                <CircularProgress />
              ) : periodClosings.length === 0 ? (
                <Alert severity="info">No period closings found. Close a month or year to see closing records.</Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Closing Date</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Period</TableCell>
                        <TableCell>Total Income</TableCell>
                        <TableCell>Total Expenses</TableCell>
                        <TableCell>Net Surplus</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {periodClosings.map((closing) => (
                        <TableRow key={closing.id}>
                          <TableCell>{new Date(closing.closing_date).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={closing.closing_type === 'month_end' ? 'Month End' : 'Year End'}
                              color={getClosingTypeColor(closing.closing_type)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {closing.period_start && closing.period_end
                              ? `${new Date(closing.period_start).toLocaleDateString()} - ${new Date(closing.period_end).toLocaleDateString()}`
                              : 'N/A'}
                          </TableCell>
                          <TableCell>₹{closing.total_income?.toLocaleString() || '0'}</TableCell>
                          <TableCell>₹{closing.total_expenses?.toLocaleString() || '0'}</TableCell>
                          <TableCell>
                            <Typography
                              color={closing.net_surplus >= 0 ? 'success.main' : 'error.main'}
                            >
                              ₹{Math.abs(closing.net_surplus || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={closing.status}
                              color={getStatusColor(closing.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              onClick={() => fetchClosingSummary(closing.id)}
                            >
                              View Summary
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </Paper>

        {/* Create Year Dialog */}
        <Dialog open={yearDialogOpen} onClose={() => setYearDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create Financial Year</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Year Code"
                  value={yearForm.year_code}
                  onChange={(e) => setYearForm({ ...yearForm, year_code: e.target.value })}
                  helperText="e.g., FY2024-25"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Start Date"
                  type="date"
                  value={yearForm.start_date}
                  onChange={(e) => setYearForm({ ...yearForm, start_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="End Date"
                  type="date"
                  value={yearForm.end_date}
                  onChange={(e) => setYearForm({ ...yearForm, end_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setYearDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleCreateYear}
              disabled={loading || !yearForm.year_code || !yearForm.start_date || !yearForm.end_date}
            >
              {loading ? <CircularProgress size={20} /> : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Close Month Dialog */}
        <Dialog open={monthCloseDialogOpen} onClose={() => setMonthCloseDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Close Month</DialogTitle>
          <DialogContent>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Closing a month will create closing entries and lock the period. This action cannot be undone.
            </Alert>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Financial Year"
                  value={activeYear?.year_code || ''}
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Closing Date"
                  type="date"
                  value={monthCloseForm.closing_date}
                  onChange={(e) => setMonthCloseForm({ ...monthCloseForm, closing_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  helperText="Last day of the month to close"
                  required
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setMonthCloseDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              color="warning"
              onClick={handleCloseMonth}
              disabled={loading || !monthCloseForm.closing_date}
            >
              {loading ? <CircularProgress size={20} /> : 'Close Month'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Close Year Dialog */}
        <Dialog open={yearCloseDialogOpen} onClose={() => setYearCloseDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Close Financial Year</DialogTitle>
          <DialogContent>
            <Alert severity="error" sx={{ mb: 2 }}>
              Closing a financial year is a critical operation. All months must be closed first. This action cannot be undone.
            </Alert>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Financial Year"
                  value={activeYear?.year_code || ''}
                  disabled
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Closing Date"
                  type="date"
                  value={yearCloseForm.closing_date || activeYear?.end_date || ''}
                  onChange={(e) => setYearCloseForm({ ...yearCloseForm, closing_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                  helperText="Last day of the financial year"
                  required
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setYearCloseDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              color="error"
              onClick={handleCloseYear}
              disabled={loading || !yearCloseForm.closing_date}
            >
              {loading ? <CircularProgress size={20} /> : 'Close Year'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Summary Dialog */}
        <Dialog open={summaryDialogOpen} onClose={() => setSummaryDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Closing Summary</DialogTitle>
          <DialogContent>
            {closingSummary && (
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Total Income</Typography>
                    <Typography variant="h6">₹{closingSummary.total_income?.toLocaleString() || '0'}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Total Expenses</Typography>
                    <Typography variant="h6">₹{closingSummary.total_expenses?.toLocaleString() || '0'}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Net Surplus/Deficit</Typography>
                    <Typography
                      variant="h4"
                      color={closingSummary.net_surplus >= 0 ? 'success.main' : 'error.main'}
                    >
                      ₹{Math.abs(closingSummary.net_surplus || 0).toLocaleString()}
                    </Typography>
                  </Grid>
                  {closingSummary.journal_entry_number && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">Closing Entry</Typography>
                      <Typography variant="body1">{closingSummary.journal_entry_number}</Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSummaryDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default FinancialClosing;

