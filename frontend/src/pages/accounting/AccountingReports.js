import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  TextField,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import Layout from '../../components/Layout';
import SummarizeIcon from '@mui/icons-material/Summarize';
import DownloadIcon from '@mui/icons-material/Download';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function AccountingReports() {
  const [activeTab, setActiveTab] = useState(0);
  const [trialBalance, setTrialBalance] = useState(null);
  const [ledger, setLedger] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 3, 1)); // April 1st
  const [toDate, setToDate] = useState(new Date());
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/accounts/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setAccounts(data);
    } catch (error) {
      console.error('Error fetching accounts:', error);
    }
  };

  const fetchTrialBalance = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const asOfDate = toDate.toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/reports/trial-balance?as_of_date=${asOfDate}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setTrialBalance(data);
    } catch (error) {
      console.error('Error fetching trial balance:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLedger = async () => {
    if (!selectedAccount) {
      alert('Please select an account');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const fromDateStr = fromDate.toISOString().split('T')[0];
      const toDateStr = toDate.toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/reports/ledger/${selectedAccount}?from_date=${fromDateStr}&to_date=${toDateStr}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setLedger(data);
    } catch (error) {
      console.error('Error fetching ledger:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <SummarizeIcon sx={{ fontSize: 40, mr: 2, color: '#FF9933' }} />
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            Accounting Reports
          </Typography>
        </Box>

        <Paper>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab label="Trial Balance" />
            <Tab label="Account Ledger" />
          </Tabs>

          {/* Trial Balance Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="As of Date"
                    value={toDate}
                    onChange={(newValue) => setToDate(newValue)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  variant="contained"
                  onClick={fetchTrialBalance}
                  disabled={loading}
                  sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                >
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
              </Grid>
            </Grid>

            {trialBalance && (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Trial Balance as of {new Date(trialBalance.as_of_date).toLocaleDateString()}
                </Alert>

                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Account Code</strong></TableCell>
                        <TableCell><strong>Account Name</strong></TableCell>
                        <TableCell align="right"><strong>Debit (₹)</strong></TableCell>
                        <TableCell align="right"><strong>Credit (₹)</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trialBalance.accounts.map((account) => (
                        <TableRow key={account.account_id}>
                          <TableCell>{account.account_code}</TableCell>
                          <TableCell>{account.account_name}</TableCell>
                          <TableCell align="right">
                            {account.debit_balance > 0 ? account.debit_balance.toFixed(2) : '-'}
                          </TableCell>
                          <TableCell align="right">
                            {account.credit_balance > 0 ? account.credit_balance.toFixed(2) : '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                      <TableRow sx={{ bgcolor: '#FFF3E0', fontWeight: 'bold' }}>
                        <TableCell colSpan={2}><strong>TOTAL</strong></TableCell>
                        <TableCell align="right">
                          <strong>₹{trialBalance.total_debits.toFixed(2)}</strong>
                        </TableCell>
                        <TableCell align="right">
                          <strong>₹{trialBalance.total_credits.toFixed(2)}</strong>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>

                {trialBalance.total_debits !== trialBalance.total_credits && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    ⚠️ Trial Balance is not balanced! Debits and Credits do not match.
                  </Alert>
                )}
              </>
            )}
          </TabPanel>

          {/* Account Ledger Tab */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Select Account</InputLabel>
                  <Select
                    value={selectedAccount}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                    label="Select Account"
                  >
                    {accounts.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.account_code} - {account.account_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="From Date"
                    value={fromDate}
                    onChange={(newValue) => setFromDate(newValue)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} md={3}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="To Date"
                    value={toDate}
                    onChange={(newValue) => setToDate(newValue)}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  variant="contained"
                  onClick={fetchLedger}
                  disabled={loading || !selectedAccount}
                  fullWidth
                  sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                >
                  {loading ? 'Loading...' : 'View Ledger'}
                </Button>
              </Grid>
            </Grid>

            {ledger && (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Ledger for {ledger.account_code} - {ledger.account_name}
                  <br />
                  Period: {new Date(ledger.from_date).toLocaleDateString()} to {new Date(ledger.to_date).toLocaleDateString()}
                </Alert>

                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Date</strong></TableCell>
                        <TableCell><strong>Entry #</strong></TableCell>
                        <TableCell><strong>Description</strong></TableCell>
                        <TableCell align="right"><strong>Debit (₹)</strong></TableCell>
                        <TableCell align="right"><strong>Credit (₹)</strong></TableCell>
                        <TableCell align="right"><strong>Balance (₹)</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {/* Opening Balance */}
                      <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                        <TableCell colSpan={5}><strong>Opening Balance</strong></TableCell>
                        <TableCell align="right">
                          <strong>₹{ledger.opening_balance.toFixed(2)}</strong>
                        </TableCell>
                      </TableRow>

                      {/* Transactions */}
                      {ledger.transactions.map((txn, index) => (
                        <TableRow key={index}>
                          <TableCell>{new Date(txn.entry_date).toLocaleDateString()}</TableCell>
                          <TableCell>{txn.entry_number}</TableCell>
                          <TableCell>{txn.description}</TableCell>
                          <TableCell align="right">
                            {txn.debit_amount > 0 ? txn.debit_amount.toFixed(2) : '-'}
                          </TableCell>
                          <TableCell align="right">
                            {txn.credit_amount > 0 ? txn.credit_amount.toFixed(2) : '-'}
                          </TableCell>
                          <TableCell align="right">{txn.running_balance.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}

                      {/* Closing Balance */}
                      <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                        <TableCell colSpan={5}><strong>Closing Balance</strong></TableCell>
                        <TableCell align="right">
                          <strong>₹{ledger.closing_balance.toFixed(2)}</strong>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </>
            )}
          </TabPanel>
        </Paper>
      </Box>
    </Layout>
  );
}

export default AccountingReports;
