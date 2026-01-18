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
  const [profitLoss, setProfitLoss] = useState(null);
  const [categoryIncome, setCategoryIncome] = useState(null);
  const [topDonors, setTopDonors] = useState(null);
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

  const fetchProfitLoss = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const fromDateStr = fromDate.toISOString().split('T')[0];
      const toDateStr = toDate.toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/reports/profit-loss?from_date=${fromDateStr}&to_date=${toDateStr}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setProfitLoss(data);
    } catch (error) {
      console.error('Error fetching profit & loss:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategoryIncome = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const fromDateStr = fromDate.toISOString().split('T')[0];
      const toDateStr = toDate.toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/reports/category-income?from_date=${fromDateStr}&to_date=${toDateStr}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setCategoryIncome(data);
    } catch (error) {
      console.error('Error fetching category income:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTopDonors = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const fromDateStr = fromDate.toISOString().split('T')[0];
      const toDateStr = toDate.toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/reports/top-donors?from_date=${fromDateStr}&to_date=${toDateStr}&limit=10`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setTopDonors(data);
    } catch (error) {
      console.error('Error fetching top donors:', error);
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
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Trial Balance" />
            <Tab label="Account Ledger" />
            <Tab label="Profit & Loss" />
            <Tab label="Category Income" />
            <Tab label="Top Donors" />
          </Tabs>

          {/* Trial Balance Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <TextField
                  label="As of Date"
                  type="date"
                  value={toDate.toISOString().split('T')[0]}
                  onChange={(e) => setToDate(new Date(e.target.value))}
                  fullWidth
                  InputLabelProps={{ shrink: true }}
                />
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

          {/* Profit & Loss Tab */}
          <TabPanel value={activeTab} index={2}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
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
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  onClick={fetchProfitLoss}
                  disabled={loading}
                  sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                >
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
              </Grid>
            </Grid>

            {profitLoss && (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Profit & Loss Statement
                  <br />
                  Period: {new Date(profitLoss.from_date).toLocaleDateString()} to {new Date(profitLoss.to_date).toLocaleDateString()}
                </Alert>

                {/* Income Section */}
                <Typography variant="h6" sx={{ mt: 2, mb: 1, bgcolor: '#FFF3E0', p: 1 }}>
                  <strong>INCOME</strong>
                </Typography>
                {profitLoss.income_groups.map((group, idx) => (
                  <Box key={idx} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {group.category_name}
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableBody>
                          {group.accounts.map((acc, accIdx) => (
                            <TableRow key={`${group.category_name}-${acc.account_code}-${accIdx}`}>
                              <TableCell sx={{ pl: 4 }}>{acc.account_code}</TableCell>
                              <TableCell>{acc.account_name}</TableCell>
                              <TableCell align="right">₹{acc.amount.toFixed(2)}</TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                            <TableCell colSpan={2} sx={{ pl: 4 }}>
                              <strong>Total {group.category_name}</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>₹{group.total.toFixed(2)}</strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                ))}
                <Box sx={{ bgcolor: '#FFF3E0', p: 2, mb: 3 }}>
                  <Grid container>
                    <Grid item xs={8}>
                      <Typography variant="h6"><strong>TOTAL INCOME</strong></Typography>
                    </Grid>
                    <Grid item xs={4} sx={{ textAlign: 'right' }}>
                      <Typography variant="h6"><strong>₹{profitLoss.total_income.toFixed(2)}</strong></Typography>
                    </Grid>
                  </Grid>
                </Box>

                {/* Expenses Section */}
                <Typography variant="h6" sx={{ mt: 2, mb: 1, bgcolor: '#FFF3E0', p: 1 }}>
                  <strong>EXPENSES</strong>
                </Typography>
                {profitLoss.expense_groups.map((group, idx) => (
                  <Box key={idx} sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {group.category_name}
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableBody>
                          {group.accounts.map((acc, accIdx) => (
                            <TableRow key={`${group.category_name}-${acc.account_code}-${accIdx}`}>
                              <TableCell sx={{ pl: 4 }}>{acc.account_code}</TableCell>
                              <TableCell>{acc.account_name}</TableCell>
                              <TableCell align="right">₹{acc.amount.toFixed(2)}</TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                            <TableCell colSpan={2} sx={{ pl: 4 }}>
                              <strong>Total {group.category_name}</strong>
                            </TableCell>
                            <TableCell align="right">
                              <strong>₹{group.total.toFixed(2)}</strong>
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                ))}
                <Box sx={{ bgcolor: '#FFF3E0', p: 2, mb: 3 }}>
                  <Grid container>
                    <Grid item xs={8}>
                      <Typography variant="h6"><strong>TOTAL EXPENSES</strong></Typography>
                    </Grid>
                    <Grid item xs={4} sx={{ textAlign: 'right' }}>
                      <Typography variant="h6"><strong>₹{profitLoss.total_expenses.toFixed(2)}</strong></Typography>
                    </Grid>
                  </Grid>
                </Box>

                {/* Net Surplus/Deficit */}
                <Box sx={{ bgcolor: profitLoss.net_surplus >= 0 ? '#C8E6C9' : '#FFCDD2', p: 2 }}>
                  <Grid container>
                    <Grid item xs={8}>
                      <Typography variant="h5">
                        <strong>{profitLoss.net_surplus >= 0 ? 'NET SURPLUS' : 'NET DEFICIT'}</strong>
                      </Typography>
                    </Grid>
                    <Grid item xs={4} sx={{ textAlign: 'right' }}>
                      <Typography variant="h5">
                        <strong>₹{Math.abs(profitLoss.net_surplus).toFixed(2)}</strong>
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              </>
            )}
          </TabPanel>

          {/* Category Income Tab */}
          <TabPanel value={activeTab} index={3}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
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
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  onClick={fetchCategoryIncome}
                  disabled={loading}
                  sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                >
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
              </Grid>
            </Grid>

            {categoryIncome && (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Category-wise Income Report
                  <br />
                  Period: {new Date(categoryIncome.from_date).toLocaleDateString()} to {new Date(categoryIncome.to_date).toLocaleDateString()}
                  <br />
                  Total Income: ₹{categoryIncome.total_income.toFixed(2)}
                </Alert>

                {/* Donation Income */}
                <Typography variant="h6" sx={{ mt: 2, mb: 1, bgcolor: '#FFF3E0', p: 1 }}>
                  <strong>DONATION INCOME</strong>
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Code</strong></TableCell>
                        <TableCell><strong>Category</strong></TableCell>
                        <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                        <TableCell align="right"><strong>%</strong></TableCell>
                        <TableCell align="right"><strong>Transactions</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {categoryIncome.donation_income.map((item, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{item.account_code}</TableCell>
                          <TableCell>{item.account_name}</TableCell>
                          <TableCell align="right">₹{item.amount.toFixed(2)}</TableCell>
                          <TableCell align="right">{item.percentage}%</TableCell>
                          <TableCell align="right">{item.transaction_count}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Seva Income */}
                <Typography variant="h6" sx={{ mt: 3, mb: 1, bgcolor: '#FFF3E0', p: 1 }}>
                  <strong>SEVA INCOME</strong>
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Code</strong></TableCell>
                        <TableCell><strong>Seva Type</strong></TableCell>
                        <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                        <TableCell align="right"><strong>%</strong></TableCell>
                        <TableCell align="right"><strong>Bookings</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {categoryIncome.seva_income.map((item, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{item.account_code}</TableCell>
                          <TableCell>{item.account_name}</TableCell>
                          <TableCell align="right">₹{item.amount.toFixed(2)}</TableCell>
                          <TableCell align="right">{item.percentage}%</TableCell>
                          <TableCell align="right">{item.transaction_count}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>

                {/* Other Income */}
                {categoryIncome.other_income.length > 0 && (
                  <>
                    <Typography variant="h6" sx={{ mt: 3, mb: 1, bgcolor: '#FFF3E0', p: 1 }}>
                      <strong>OTHER INCOME</strong>
                    </Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                            <TableCell><strong>Code</strong></TableCell>
                            <TableCell><strong>Category</strong></TableCell>
                            <TableCell align="right"><strong>Amount (₹)</strong></TableCell>
                            <TableCell align="right"><strong>%</strong></TableCell>
                            <TableCell align="right"><strong>Transactions</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {categoryIncome.other_income.map((item, idx) => (
                            <TableRow key={idx}>
                              <TableCell>{item.account_code}</TableCell>
                              <TableCell>{item.account_name}</TableCell>
                              <TableCell align="right">₹{item.amount.toFixed(2)}</TableCell>
                              <TableCell align="right">{item.percentage}%</TableCell>
                              <TableCell align="right">{item.transaction_count}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}
              </>
            )}
          </TabPanel>

          {/* Top Donors Tab */}
          <TabPanel value={activeTab} index={4}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
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
              <Grid item xs={12} md={3}>
                <Button
                  variant="contained"
                  onClick={fetchTopDonors}
                  disabled={loading}
                  sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                >
                  {loading ? 'Loading...' : 'Generate Report'}
                </Button>
              </Grid>
            </Grid>

            {topDonors && (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Top {topDonors.donors.length} Donors
                  <br />
                  Period: {new Date(topDonors.from_date).toLocaleDateString()} to {new Date(topDonors.to_date).toLocaleDateString()}
                  <br />
                  Total Donations: ₹{topDonors.total_amount.toFixed(2)} from {topDonors.total_donors} donors
                </Alert>

                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                        <TableCell><strong>Rank</strong></TableCell>
                        <TableCell><strong>Devotee Name</strong></TableCell>
                        <TableCell align="right"><strong>Total Donated (₹)</strong></TableCell>
                        <TableCell align="right"><strong>Donations</strong></TableCell>
                        <TableCell><strong>Last Donation</strong></TableCell>
                        <TableCell><strong>Categories</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {topDonors.donors.map((donor, idx) => (
                        <TableRow key={donor.devotee_id}>
                          <TableCell>
                            <Box
                              sx={{
                                width: 30,
                                height: 30,
                                borderRadius: '50%',
                                bgcolor: idx === 0 ? '#FFD700' : idx === 1 ? '#C0C0C0' : idx === 2 ? '#CD7F32' : '#FF9933',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontWeight: 'bold',
                              }}
                            >
                              {idx + 1}
                            </Box>
                          </TableCell>
                          <TableCell><strong>{donor.devotee_name}</strong></TableCell>
                          <TableCell align="right">
                            <Typography variant="h6" sx={{ color: '#FF9933' }}>
                              ₹{donor.total_donated.toFixed(2)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">{donor.donation_count}</TableCell>
                          <TableCell>{new Date(donor.last_donation_date).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                              {donor.categories.map((cat, catIdx) => (
                                <Box
                                  key={catIdx}
                                  sx={{
                                    bgcolor: '#FFF3E0',
                                    px: 1,
                                    py: 0.5,
                                    borderRadius: 1,
                                    fontSize: '0.75rem',
                                  }}
                                >
                                  {cat}
                                </Box>
                              ))}
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
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
