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
  Chip,
  IconButton,
  Collapse,
  Button,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
} from '@mui/material';
import Layout from '../../components/Layout';
import ReceiptIcon from '@mui/icons-material/Receipt';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

function JournalEntryRow({ entry }) {
  const [open, setOpen] = useState(false);

  const getStatusColor = (status) => {
    switch (status) {
      case 'POSTED':
        return 'success';
      case 'DRAFT':
        return 'warning';
      case 'CANCELLED':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{entry.entry_number}</TableCell>
        <TableCell>{new Date(entry.entry_date).toLocaleDateString()}</TableCell>
        <TableCell>{entry.narration}</TableCell>
        <TableCell align="right">₹{entry.total_amount.toFixed(2)}</TableCell>
        <TableCell>
          <Chip label={entry.status} color={getStatusColor(entry.status)} size="small" />
        </TableCell>
        <TableCell>{entry.reference_type || '-'}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 2 }}>
              <Typography variant="h6" gutterBottom>
                Journal Lines
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell><strong>Account</strong></TableCell>
                    <TableCell><strong>Description</strong></TableCell>
                    <TableCell align="right"><strong>Debit (₹)</strong></TableCell>
                    <TableCell align="right"><strong>Credit (₹)</strong></TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {entry.journal_lines.map((line, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        {line.account_code} - {line.account_name}
                      </TableCell>
                      <TableCell>{line.description}</TableCell>
                      <TableCell align="right">
                        {line.debit_amount > 0 ? line.debit_amount.toFixed(2) : '-'}
                      </TableCell>
                      <TableCell align="right">
                        {line.credit_amount > 0 ? line.credit_amount.toFixed(2) : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                    <TableCell colSpan={2}><strong>TOTAL</strong></TableCell>
                    <TableCell align="right">
                      <strong>
                        ₹{entry.journal_lines.reduce((sum, line) => sum + line.debit_amount, 0).toFixed(2)}
                      </strong>
                    </TableCell>
                    <TableCell align="right">
                      <strong>
                        ₹{entry.journal_lines.reduce((sum, line) => sum + line.credit_amount, 0).toFixed(2)}
                      </strong>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
}

function JournalEntries() {
  const [entries, setEntries] = useState([]);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 3, 1)); // April 1st
  const [toDate, setToDate] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [accounts, setAccounts] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Form state
  const [entryDate, setEntryDate] = useState(new Date().toISOString().split('T')[0]);
  const [narration, setNarration] = useState('');
  const [referenceType, setReferenceType] = useState('EXPENSE');
  const [referenceNumber, setReferenceNumber] = useState('');
  const [journalLines, setJournalLines] = useState([
    { account_id: '', debit_amount: '', credit_amount: '', description: '' },
    { account_id: '', debit_amount: '', credit_amount: '', description: '' },
  ]);

  useEffect(() => {
    fetchEntries();
    fetchAccounts();
  }, []);

  const fetchEntries = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const fromDateStr = fromDate.toISOString().split('T')[0];
      const toDateStr = toDate.toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/?from_date=${fromDateStr}&to_date=${toDateStr}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setEntries(data);
    } catch (error) {
      console.error('Error fetching journal entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/accounts/`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      // Flatten the hierarchical accounts for the dropdown
      const flattenAccounts = (accs, result = []) => {
        accs.forEach(acc => {
          result.push(acc);
          if (acc.sub_accounts && acc.sub_accounts.length > 0) {
            flattenAccounts(acc.sub_accounts, result);
          }
        });
        return result;
      };
      setAccounts(flattenAccounts(data));
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const handleAddLine = () => {
    setJournalLines([...journalLines, { account_id: '', debit_amount: '', credit_amount: '', description: '' }]);
  };

  const handleRemoveLine = (index) => {
    if (journalLines.length > 2) {
      const newLines = journalLines.filter((_, i) => i !== index);
      setJournalLines(newLines);
    }
  };

  const handleLineChange = (index, field, value) => {
    const newLines = [...journalLines];
    newLines[index][field] = value;
    setJournalLines(newLines);
  };

  const calculateTotals = () => {
    const totalDebit = journalLines.reduce((sum, line) => sum + (parseFloat(line.debit_amount) || 0), 0);
    const totalCredit = journalLines.reduce((sum, line) => sum + (parseFloat(line.credit_amount) || 0), 0);
    return { totalDebit, totalCredit };
  };

  const handleCreateEntry = async () => {
    try {
      const { totalDebit, totalCredit } = calculateTotals();
      if (totalDebit !== totalCredit) {
        setSnackbar({ open: true, message: 'Total debits must equal total credits!', severity: 'error' });
        return;
      }

      if (totalDebit === 0) {
        setSnackbar({ open: true, message: 'Entry cannot have zero amount!', severity: 'error' });
        return;
      }

      const token = localStorage.getItem('token');
      const payload = {
        entry_date: entryDate,
        narration,
        reference_type: referenceType,
        reference_number: referenceNumber || undefined,
        journal_lines: journalLines.map(line => ({
          account_id: parseInt(line.account_id),
          debit_amount: parseFloat(line.debit_amount) || 0,
          credit_amount: parseFloat(line.credit_amount) || 0,
          description: line.description,
        })),
      };

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/journal-entries/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        setSnackbar({ open: true, message: 'Journal entry created successfully!', severity: 'success' });
        setOpenDialog(false);
        resetForm();
        fetchEntries();
      } else {
        const error = await response.json();
        setSnackbar({ open: true, message: error.detail || 'Failed to create entry', severity: 'error' });
      }
    } catch (error) {
      console.error('Error creating journal entry:', error);
      setSnackbar({ open: true, message: 'Error creating journal entry', severity: 'error' });
    }
  };

  const resetForm = () => {
    setEntryDate(new Date().toISOString().split('T')[0]);
    setNarration('');
    setReferenceType('EXPENSE');
    setReferenceNumber('');
    setJournalLines([
      { account_id: '', debit_amount: '', credit_amount: '', description: '' },
      { account_id: '', debit_amount: '', credit_amount: '', description: '' },
    ]);
  };

  const { totalDebit, totalCredit } = calculateTotals();

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <ReceiptIcon sx={{ fontSize: 40, mr: 2, color: '#FF9933' }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
              Journal Entries
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
            sx={{ bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
          >
            Create Entry
          </Button>
        </Box>

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                label="From Date"
                type="date"
                value={fromDate.toISOString().split('T')[0]}
                onChange={(e) => setFromDate(new Date(e.target.value))}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                label="To Date"
                type="date"
                value={toDate.toISOString().split('T')[0]}
                onChange={(e) => setToDate(new Date(e.target.value))}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                onClick={fetchEntries}
                disabled={loading}
                fullWidth
                sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
              >
                {loading ? 'Loading...' : 'Filter'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Entries Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#FF9933' }}>
                  <TableCell sx={{ color: 'white', width: 50 }}></TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Entry #</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Narration</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">Amount</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Type</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography>Loading journal entries...</Typography>
                    </TableCell>
                  </TableRow>
                ) : entries.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary">No journal entries found for this period</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  entries.map((entry) => <JournalEntryRow key={entry.id} entry={entry} />)
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Create Entry Dialog */}
        <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>Create Journal Entry</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Entry Date"
                  type="date"
                  value={entryDate}
                  onChange={(e) => setEntryDate(e.target.value)}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Reference Type</InputLabel>
                  <Select
                    value={referenceType}
                    onChange={(e) => setReferenceType(e.target.value)}
                    label="Reference Type"
                  >
                    <MenuItem value="EXPENSE">Expense</MenuItem>
                    <MenuItem value="INCOME">Income</MenuItem>
                    <MenuItem value="TRANSFER">Transfer</MenuItem>
                    <MenuItem value="ADJUSTMENT">Adjustment</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Narration"
                  value={narration}
                  onChange={(e) => setNarration(e.target.value)}
                  fullWidth
                  required
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Reference Number (Optional)"
                  value={referenceNumber}
                  onChange={(e) => setReferenceNumber(e.target.value)}
                  fullWidth
                />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>Journal Lines</Typography>
                {journalLines.map((line, index) => (
                  <Paper key={index} sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Account</InputLabel>
                          <Select
                            value={line.account_id}
                            onChange={(e) => handleLineChange(index, 'account_id', e.target.value)}
                            label="Account"
                          >
                            {accounts.map((acc) => (
                              <MenuItem key={acc.id} value={acc.id}>
                                {acc.account_code} - {acc.account_name}
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          label="Debit Amount"
                          type="number"
                          value={line.debit_amount}
                          onChange={(e) => handleLineChange(index, 'debit_amount', e.target.value)}
                          fullWidth
                          size="small"
                          inputProps={{ step: '0.01', min: '0' }}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <TextField
                          label="Credit Amount"
                          type="number"
                          value={line.credit_amount}
                          onChange={(e) => handleLineChange(index, 'credit_amount', e.target.value)}
                          fullWidth
                          size="small"
                          inputProps={{ step: '0.01', min: '0' }}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <IconButton
                          color="error"
                          onClick={() => handleRemoveLine(index)}
                          disabled={journalLines.length <= 2}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          label="Description"
                          value={line.description}
                          onChange={(e) => handleLineChange(index, 'description', e.target.value)}
                          fullWidth
                          size="small"
                        />
                      </Grid>
                    </Grid>
                  </Paper>
                ))}

                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={handleAddLine}
                  sx={{ mb: 2 }}
                >
                  Add Line
                </Button>

                <Box sx={{ bgcolor: '#fff3e0', p: 2, borderRadius: 1 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2">Total Debit: ₹{totalDebit.toFixed(2)}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Total Credit: ₹{totalCredit.toFixed(2)}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography
                        variant="body2"
                        color={totalDebit === totalCredit && totalDebit > 0 ? 'success.main' : 'error.main'}
                      >
                        {totalDebit === totalCredit && totalDebit > 0
                          ? '✓ Entry is balanced'
                          : '✗ Entry must be balanced (debits = credits)'}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button
              variant="contained"
              onClick={handleCreateEntry}
              disabled={totalDebit !== totalCredit || totalDebit === 0}
              sx={{ bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
            >
              Create Entry
            </Button>
          </DialogActions>
        </Dialog>

        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </Layout>
  );
}

export default JournalEntries;
