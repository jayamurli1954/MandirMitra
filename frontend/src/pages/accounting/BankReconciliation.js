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
  IconButton,
  Checkbox,
  LinearProgress,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import LinkIcon from '@mui/icons-material/Link';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

function BankReconciliation() {
  const { showSuccess, showError } = useNotification();
  const [loading, setLoading] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  
  // Data
  const [bankAccounts, setBankAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [statements, setStatements] = useState([]);
  const [selectedStatement, setSelectedStatement] = useState(null);
  const [statementEntries, setStatementEntries] = useState([]);
  const [unmatchedEntries, setUnmatchedEntries] = useState([]);
  const [reconciliationSummary, setReconciliationSummary] = useState(null);
  
  // Dialogs
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [matchDialogOpen, setMatchDialogOpen] = useState(false);
  const [reconcileDialogOpen, setReconcileDialogOpen] = useState(false);
  
  // Forms
  const [uploadForm, setUploadForm] = useState({
    account_id: '',
    statement_date: new Date().toISOString().split('T')[0],
    file: null,
  });
  
  const [matchForm, setMatchForm] = useState({
    statement_entry_id: null,
    journal_line_id: null,
    notes: '',
  });

  useEffect(() => {
    fetchBankAccounts();
  }, []);

  useEffect(() => {
    if (selectedAccount) {
      fetchStatements(selectedAccount.id);
    }
  }, [selectedAccount]);

  useEffect(() => {
    if (selectedStatement) {
      fetchStatementEntries(selectedStatement.id);
      fetchReconciliationSummary(selectedStatement.id);
    }
  }, [selectedStatement]);

  const fetchBankAccounts = async () => {
    try {
      const response = await api.get('/api/v1/bank-reconciliation/accounts');
      setBankAccounts(response.data);
      if (response.data.length > 0) {
        setSelectedAccount(response.data[0]);
      }
    } catch (err) {
      showError('Failed to fetch bank accounts');
    }
  };

  const fetchStatements = async (accountId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/bank-reconciliation/statements?account_id=${accountId}`);
      setStatements(response.data);
    } catch (err) {
      showError('Failed to fetch statements');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatementEntries = async (statementId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/v1/bank-reconciliation/statements/${statementId}/entries`);
      setStatementEntries(response.data);
      
      // Get unmatched entries
      const unmatched = response.data.filter(e => !e.is_matched);
      setUnmatchedEntries(unmatched);
    } catch (err) {
      showError('Failed to fetch statement entries');
    } finally {
      setLoading(false);
    }
  };

  const fetchReconciliationSummary = async (statementId) => {
    try {
      const response = await api.get(`/api/v1/bank-reconciliation/statements/${statementId}/summary`);
      setReconciliationSummary(response.data);
    } catch (err) {
      console.error('Failed to fetch reconciliation summary');
    }
  };

  const handleFileUpload = async () => {
    if (!uploadForm.file || !uploadForm.account_id) {
      showError('Please select account and file');
      return;
    }

    try {
      setLoading(true);
      const formData = new FormData();
      formData.append('file', uploadForm.file);
      formData.append('account_id', uploadForm.account_id);
      formData.append('statement_date', uploadForm.statement_date);

      const response = await api.post('/api/v1/bank-reconciliation/statements/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      showSuccess('Bank statement imported successfully');
      setUploadDialogOpen(false);
      setUploadForm({
        account_id: '',
        statement_date: new Date().toISOString().split('T')[0],
        file: null,
      });
      
      if (selectedAccount) {
        fetchStatements(selectedAccount.id);
      }
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to import statement');
    } finally {
      setLoading(false);
    }
  };

  const handleMatchEntry = async (entryId) => {
    // Get available journal lines for matching
    try {
      const response = await api.get(`/api/v1/bank-reconciliation/statements/${selectedStatement.id}/unmatched-book-entries`);
      // Open match dialog with available options
      setMatchForm({
        statement_entry_id: entryId,
        journal_line_id: '',
        notes: '',
      });
      setMatchDialogOpen(true);
    } catch (err) {
      showError('Failed to fetch unmatched book entries');
    }
  };

  const handleConfirmMatch = async () => {
    if (!matchForm.journal_line_id) {
      showError('Please select a journal line to match');
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/v1/bank-reconciliation/match', {
        statement_entry_id: matchForm.statement_entry_id,
        journal_line_id: matchForm.journal_line_id,
        notes: matchForm.notes,
      });

      showSuccess('Entry matched successfully');
      setMatchDialogOpen(false);
      fetchStatementEntries(selectedStatement.id);
      fetchReconciliationSummary(selectedStatement.id);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to match entry');
    } finally {
      setLoading(false);
    }
  };

  const handleReconcile = async () => {
    if (!selectedStatement) {
      showError('Please select a statement');
      return;
    }

    try {
      setLoading(true);
      await api.post('/api/v1/bank-reconciliation/reconcile', {
        account_id: selectedAccount.id,
        statement_id: selectedStatement.id,
        reconciliation_date: new Date().toISOString().split('T')[0],
      });

      showSuccess('Reconciliation completed successfully');
      setReconcileDialogOpen(false);
      fetchStatements(selectedAccount.id);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to reconcile');
    } finally {
      setLoading(false);
    }
  };

  const getEntryTypeColor = (type) => {
    const colors = {
      deposit: 'success',
      withdrawal: 'error',
      charges: 'warning',
      interest: 'info',
    };
    return colors[type] || 'default';
  };

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Bank Reconciliation
          </Typography>
          <Button
            variant="contained"
            startIcon={<UploadFileIcon />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Import Statement
          </Button>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Select Bank Account</Typography>
                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Bank Account</InputLabel>
                  <Select
                    value={selectedAccount?.id || ''}
                    onChange={(e) => {
                      const account = bankAccounts.find(a => a.id === e.target.value);
                      setSelectedAccount(account);
                      setSelectedStatement(null);
                    }}
                    label="Bank Account"
                  >
                    {bankAccounts.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name} ({account.code})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={9}>
            <Paper>
              <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
                <Tab label="Statements" />
                <Tab label="Reconciliation" />
              </Tabs>

              {tabValue === 0 && (
                <Box sx={{ p: 3 }}>
                  {loading ? (
                    <CircularProgress />
                  ) : statements.length === 0 ? (
                    <Alert severity="info">No statements found. Import your first bank statement to get started.</Alert>
                  ) : (
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Statement Date</TableCell>
                            <TableCell>From Date</TableCell>
                            <TableCell>To Date</TableCell>
                            <TableCell>Opening Balance</TableCell>
                            <TableCell>Closing Balance</TableCell>
                            <TableCell>Entries</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {statements.map((statement) => (
                            <TableRow key={statement.id}>
                              <TableCell>{new Date(statement.statement_date).toLocaleDateString()}</TableCell>
                              <TableCell>{new Date(statement.from_date).toLocaleDateString()}</TableCell>
                              <TableCell>{new Date(statement.to_date).toLocaleDateString()}</TableCell>
                              <TableCell>₹{statement.opening_balance?.toLocaleString() || '0'}</TableCell>
                              <TableCell>₹{statement.closing_balance?.toLocaleString() || '0'}</TableCell>
                              <TableCell>{statement.total_entries || 0}</TableCell>
                              <TableCell>
                                <Chip
                                  label={statement.is_reconciled ? 'Reconciled' : 'Pending'}
                                  color={statement.is_reconciled ? 'success' : 'warning'}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <Button
                                  size="small"
                                  onClick={() => {
                                    setSelectedStatement(statement);
                                    setTabValue(1);
                                  }}
                                >
                                  View
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

              {tabValue === 1 && selectedStatement && (
                <Box sx={{ p: 3 }}>
                  {reconciliationSummary && (
                    <Card sx={{ mb: 3 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>Reconciliation Summary</Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">Book Balance</Typography>
                            <Typography variant="h6">₹{reconciliationSummary.book_balance?.toLocaleString() || '0'}</Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">Bank Balance</Typography>
                            <Typography variant="h6">₹{reconciliationSummary.bank_balance?.toLocaleString() || '0'}</Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">Difference</Typography>
                            <Typography variant="h6" color={reconciliationSummary.difference === 0 ? 'success.main' : 'error.main'}>
                              ₹{Math.abs(reconciliationSummary.difference || 0).toLocaleString()}
                            </Typography>
                          </Grid>
                          <Grid item xs={6} sm={3}>
                            <Typography variant="body2" color="text.secondary">Matched</Typography>
                            <Typography variant="h6">
                              {reconciliationSummary.matched_count || 0} / {reconciliationSummary.total_count || 0}
                            </Typography>
                          </Grid>
                        </Grid>
                        {reconciliationSummary.difference === 0 && (
                          <Button
                            variant="contained"
                            color="success"
                            sx={{ mt: 2 }}
                            onClick={() => setReconcileDialogOpen(true)}
                          >
                            Complete Reconciliation
                          </Button>
                        )}
                      </CardContent>
                    </Card>
                  )}

                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>Statement Entries</Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Description</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell>Amount</TableCell>
                          <TableCell>Balance</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statementEntries.map((entry) => (
                          <TableRow key={entry.id}>
                            <TableCell>{new Date(entry.transaction_date).toLocaleDateString()}</TableCell>
                            <TableCell>{entry.description}</TableCell>
                            <TableCell>
                              <Chip
                                label={entry.entry_type}
                                color={getEntryTypeColor(entry.entry_type)}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>₹{Math.abs(entry.amount).toLocaleString()}</TableCell>
                            <TableCell>₹{entry.balance?.toLocaleString() || '0'}</TableCell>
                            <TableCell>
                              {entry.is_matched ? (
                                <CheckCircleIcon color="success" fontSize="small" />
                              ) : (
                                <CancelIcon color="error" fontSize="small" />
                              )}
                            </TableCell>
                            <TableCell>
                              {!entry.is_matched && (
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleMatchEntry(entry.id)}
                                >
                                  <LinkIcon />
                                </IconButton>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Upload Dialog */}
        <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Import Bank Statement</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Bank Account</InputLabel>
                  <Select
                    value={uploadForm.account_id}
                    onChange={(e) => setUploadForm({ ...uploadForm, account_id: e.target.value })}
                    label="Bank Account"
                  >
                    {bankAccounts.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name} ({account.code})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Statement Date"
                  type="date"
                  value={uploadForm.statement_date}
                  onChange={(e) => setUploadForm({ ...uploadForm, statement_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <Button variant="outlined" component="label" fullWidth>
                  Select CSV File
                  <input
                    type="file"
                    hidden
                    accept=".csv"
                    onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })}
                  />
                </Button>
                {uploadForm.file && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Selected: {uploadForm.file.name}
                  </Typography>
                )}
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Expected CSV format: Date, Value Date, Description, Debit, Credit, Balance, Reference
                </Typography>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleFileUpload}
              disabled={loading || !uploadForm.file || !uploadForm.account_id}
            >
              {loading ? <CircularProgress size={20} /> : 'Import'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Match Dialog */}
        <Dialog open={matchDialogOpen} onClose={() => setMatchDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Match Statement Entry</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Journal Line ID"
                  value={matchForm.journal_line_id}
                  onChange={(e) => setMatchForm({ ...matchForm, journal_line_id: e.target.value })}
                  helperText="Enter the journal line ID to match with this statement entry"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  value={matchForm.notes}
                  onChange={(e) => setMatchForm({ ...matchForm, notes: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setMatchDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleConfirmMatch}
              disabled={loading || !matchForm.journal_line_id}
            >
              {loading ? <CircularProgress size={20} /> : 'Match'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Reconcile Dialog */}
        <Dialog open={reconcileDialogOpen} onClose={() => setReconcileDialogOpen(false)}>
          <DialogTitle>Complete Reconciliation</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to complete the reconciliation? This will mark the statement as reconciled.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setReconcileDialogOpen(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleReconcile}
              disabled={loading}
            >
              {loading ? <CircularProgress size={20} /> : 'Reconcile'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default BankReconciliation;



