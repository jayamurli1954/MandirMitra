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
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  FormHelperText,
} from '@mui/material';
import Layout from '../../components/Layout';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

// Account code series guidance
const ACCOUNT_CODE_SERIES = {
  asset: {
    range: '1000-1999',
    examples: ['1100 - Cash in Hand', '1110 - Bank Accounts', '1200 - Inventory', '1300 - Fixed Assets'],
    description: 'Assets represent what the temple owns. Use codes 1000-1999.'
  },
  liability: {
    range: '2000-2999',
    examples: ['2100 - Accounts Payable', '2200 - Loans Payable', '2300 - Deposits'],
    description: 'Liabilities represent what the temple owes. Use codes 2000-2999.'
  },
  income: {
    range: '4000-4999',
    examples: ['4100 - Donations', '4200 - Seva Income', '4300 - Sponsorships'],
    description: 'Income represents money received. Use codes 4000-4999.'
  },
  expense: {
    range: '5000-5999',
    examples: ['5100 - Salaries', '5200 - Utilities', '5300 - Maintenance'],
    description: 'Expenses represent money spent. Use codes 5000-5999.'
  },
  equity: {
    range: '3000-3999',
    examples: ['3100 - Temple Fund', '3200 - Reserve Fund'],
    description: 'Equity represents temple\'s net worth. Use codes 3000-3999.'
  }
};

function AccountRow({ account, level = 0, onEdit, onCheckTransactions }) {
  const [open, setOpen] = useState(level === 0);

  const getAccountTypeColor = (type) => {
    switch (type) {
      case 'ASSET':
        return 'success';
      case 'LIABILITY':
        return 'error';
      case 'INCOME':
        return 'primary';
      case 'EXPENSE':
        return 'warning';
      case 'EQUITY':
        return 'info';
      default:
        return 'default';
    }
  };

  const getAccountTypeIcon = (type) => {
    switch (type) {
      case 'ASSET':
        return <AccountBalanceIcon fontSize="small" />;
      case 'LIABILITY':
        return <TrendingDownIcon fontSize="small" />;
      case 'INCOME':
        return <TrendingUpIcon fontSize="small" />;
      case 'EXPENSE':
        return <TrendingDownIcon fontSize="small" />;
      case 'EQUITY':
        return <AccountBalanceWalletIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const hasSubAccounts = account.sub_accounts && account.sub_accounts.length > 0;

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' }, bgcolor: level === 0 ? '#f5f5f5' : 'inherit' }}>
        <TableCell>
          {hasSubAccounts ? (
            <IconButton size="small" onClick={() => setOpen(!open)}>
              {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
            </IconButton>
          ) : (
            <Box sx={{ width: 40 }} />
          )}
        </TableCell>
        <TableCell>
          <Box sx={{ pl: level * 3, fontWeight: 'bold' }}>{account.account_code}</Box>
        </TableCell>
        <TableCell>
          <Box sx={{ pl: level * 3, fontWeight: level === 0 ? 'bold' : 'normal', display: 'flex', alignItems: 'center', gap: 1 }}>
            {account.account_name}
            {!account.is_system_account && (
              <IconButton
                size="small"
                onClick={() => onEdit(account)}
                color="primary"
                sx={{ ml: 1 }}
              >
                <EditIcon fontSize="small" />
              </IconButton>
            )}
          </Box>
        </TableCell>
        <TableCell>
          <Chip
            icon={getAccountTypeIcon(account.account_type)}
            label={account.account_type}
            size="small"
            color={getAccountTypeColor(account.account_type)}
          />
        </TableCell>
        <TableCell align="right">
          {account.is_system_account && (
            <Chip label="System" size="small" variant="outlined" />
          )}
        </TableCell>
        <TableCell>
          <Chip
            label={account.is_active ? 'Active' : 'Inactive'}
            size="small"
            color={account.is_active ? 'success' : 'default'}
          />
        </TableCell>
      </TableRow>
      {hasSubAccounts && (
        <TableRow>
          <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
            <Collapse in={open} timeout="auto" unmountOnExit>
              <Table size="small">
                <TableBody>
                  {account.sub_accounts.map((subAccount) => (
                    <AccountRow 
                      key={subAccount.id} 
                      account={subAccount} 
                      level={level + 1}
                      onEdit={onEdit}
                      onCheckTransactions={onCheckTransactions}
                    />
                  ))}
                </TableBody>
              </Table>
            </Collapse>
          </TableCell>
        </TableRow>
      )}
    </>
  );
}

function ChartOfAccounts() {
  const { showSuccess, showError } = useNotification();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    ASSET: 0,
    LIABILITY: 0,
    INCOME: 0,
    EXPENSE: 0,
    EQUITY: 0,
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [editingAccount, setEditingAccount] = useState(null);
  const [checkingTransactions, setCheckingTransactions] = useState(false);
  const [formData, setFormData] = useState({
    account_type: '',
    account_code: '',
    account_name: '',
    description: '',
    account_subtype: '',
    is_active: true,
  });

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/accounts/hierarchy');
      setAccounts(response.data || []);

      // Calculate stats
      const calculateStats = (accs) => {
        const newStats = { ASSET: 0, LIABILITY: 0, INCOME: 0, EXPENSE: 0, EQUITY: 0 };
        const countAccounts = (accounts) => {
          accounts.forEach((acc) => {
            newStats[acc.account_type]++;
            if (acc.sub_accounts && acc.sub_accounts.length > 0) {
              countAccounts(acc.sub_accounts);
            }
          });
        };
        countAccounts(accs);
        return newStats;
      };

      setStats(calculateStats(response.data || []));
    } catch (error) {
      console.error('Error fetching accounts:', error);
      showError('Error fetching accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setActiveStep(0);
    setFormData({
      account_type: '',
      account_code: '',
      account_name: '',
      description: '',
      account_subtype: '',
      is_active: true,
    });
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setActiveStep(0);
    setFormData({
      account_type: '',
      account_code: '',
      account_name: '',
      description: '',
      account_subtype: '',
      is_active: true,
    });
  };

  const handleEdit = async (account) => {
    setEditingAccount(account);
    setCheckingTransactions(true);
    
    try {
      // Check if account has transactions
      const response = await api.get(`/api/v1/accounts/${account.id}/has-transactions`);
      
      if (response.data.has_transactions) {
        showError(
          'This account has transaction history. Account name cannot be edited. ' +
          'Please create a new account and transfer the balance using a Journal Voucher.'
        );
        setCheckingTransactions(false);
        return;
      }
      
      // Can edit - open edit dialog
      setFormData({
        account_type: account.account_type,
        account_code: account.account_code,
        account_name: account.account_name,
        description: account.description || '',
        account_subtype: account.account_subtype || '',
        is_active: account.is_active,
      });
      setEditDialogOpen(true);
    } catch (err) {
      showError(err.response?.data?.detail || 'Error checking account transactions');
    } finally {
      setCheckingTransactions(false);
    }
  };

  const handleCloseEditDialog = () => {
    setEditDialogOpen(false);
    setEditingAccount(null);
    setFormData({
      account_type: '',
      account_code: '',
      account_name: '',
      description: '',
      account_subtype: '',
      is_active: true,
    });
  };

  const handleNext = () => {
    if (activeStep === 0 && !formData.account_type) {
      showError('Please select an account type');
      return;
    }
    setActiveStep(1);
  };

  const handleBack = () => {
    setActiveStep(0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.account_code || !formData.account_name) {
      showError('Please fill all required fields');
      return;
    }

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      
      if (editingAccount) {
        // Update existing account
        await api.put(`/api/v1/accounts/${editingAccount.id}`, {
          account_name: formData.account_name,
          description: formData.description,
          account_subtype: formData.account_subtype || null,
          is_active: formData.is_active,
        });
        showSuccess('Account updated successfully');
        handleCloseEditDialog();
      } else {
        // Create new account
        await api.post('/api/v1/accounts', {
          temple_id: user.temple_id,
          account_code: formData.account_code,
          account_name: formData.account_name,
          description: formData.description,
          account_type: formData.account_type,
          account_subtype: formData.account_subtype || null,
          is_active: formData.is_active,
          opening_balance_debit: 0,
          opening_balance_credit: 0,
        });
        showSuccess('Account created successfully');
        handleCloseDialog();
      }
      
      fetchAccounts();
    } catch (err) {
      showError(err.response?.data?.detail || 'Error saving account');
    }
  };

  const getAccountTypeInfo = () => {
    if (!formData.account_type) return null;
    return ACCOUNT_CODE_SERIES[formData.account_type.toLowerCase()];
  };

  const steps = ['Select Account Type', 'Enter Account Details'];

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccountTreeIcon sx={{ fontSize: 40, mr: 2, color: '#FF9933' }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
              Chart of Accounts
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleOpenDialog}
            sx={{ bgcolor: '#FF9933', '&:hover': { bgcolor: '#e6891e' } }}
          >
            Add Account
          </Button>
        </Box>

        {/* Stats */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Asset Accounts</Typography>
            <Typography variant="h4" color="success.main">{stats.ASSET}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Liability Accounts</Typography>
            <Typography variant="h4" color="error.main">{stats.LIABILITY}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Income Accounts</Typography>
            <Typography variant="h4" color="primary.main">{stats.INCOME}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Expense Accounts</Typography>
            <Typography variant="h4" color="warning.main">{stats.EXPENSE}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Equity Accounts</Typography>
            <Typography variant="h4" color="info.main">{stats.EQUITY}</Typography>
          </Paper>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            <strong>Important:</strong> Account codes cannot be changed once created. Account names can only be edited if the account has no transaction history.
          </Typography>
          <Typography variant="body2">
            If an account has transactions, create a new account and transfer the balance using a Journal Voucher.
          </Typography>
        </Alert>

        {/* Accounts Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#FF9933' }}>
                  <TableCell sx={{ color: 'white', width: 50 }}></TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Code</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Account Name</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Type</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">System</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : accounts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary">No accounts found</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  accounts.map((account) => (
                    <AccountRow 
                      key={account.id} 
                      account={account} 
                      onEdit={handleEdit}
                    />
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Add Account Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>Add New Account</DialogTitle>
          <DialogContent>
            <Stepper activeStep={activeStep} sx={{ mb: 3, mt: 2 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {activeStep === 0 && (
              <Box>
                <FormControl fullWidth sx={{ mb: 3 }}>
                  <InputLabel>Select Account Type *</InputLabel>
                  <Select
                    value={formData.account_type}
                    onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
                    label="Select Account Type *"
                  >
                    <MenuItem value="asset">Asset</MenuItem>
                    <MenuItem value="liability">Liability</MenuItem>
                    <MenuItem value="income">Income</MenuItem>
                    <MenuItem value="expense">Expense</MenuItem>
                    <MenuItem value="equity">Equity</MenuItem>
                  </Select>
                </FormControl>

                {formData.account_type && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                      Account Code Series: {getAccountTypeInfo()?.range}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      {getAccountTypeInfo()?.description}
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', mt: 1 }}>
                      Examples:
                    </Typography>
                    {getAccountTypeInfo()?.examples.map((ex, idx) => (
                      <Typography key={idx} variant="caption" display="block">
                        • {ex}
                      </Typography>
                    ))}
                  </Alert>
                )}
              </Box>
            )}

            {activeStep === 1 && (
              <Box component="form" onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Account Code *"
                  value={formData.account_code}
                  onChange={(e) => setFormData({ ...formData, account_code: e.target.value.toUpperCase() })}
                  required
                  sx={{ mb: 2 }}
                  helperText={`Use codes from ${getAccountTypeInfo()?.range} series. Code cannot be changed once saved.`}
                  inputProps={{ maxLength: 20 }}
                />
                <TextField
                  fullWidth
                  label="Account Name *"
                  value={formData.account_name}
                  onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                  required
                  sx={{ mb: 2 }}
                  helperText="Enter a descriptive name for this account"
                  inputProps={{ maxLength: 200 }}
                />
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  multiline
                  rows={3}
                  sx={{ mb: 2 }}
                  helperText="Describe what this account is used for"
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            {activeStep === 1 && (
              <Button onClick={handleBack}>Back</Button>
            )}
            <Button onClick={handleCloseDialog}>Cancel</Button>
            {activeStep === 0 ? (
              <Button onClick={handleNext} variant="contained">Next</Button>
            ) : (
              <Button onClick={handleSubmit} variant="contained" type="submit">Save Account</Button>
            )}
          </DialogActions>
        </Dialog>

        {/* Edit Account Dialog */}
        <Dialog open={editDialogOpen} onClose={handleCloseEditDialog} maxWidth="md" fullWidth>
          <DialogTitle>Edit Account</DialogTitle>
          <DialogContent>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Note:</strong> Account code cannot be changed. Only account name, description, and status can be edited.
              </Typography>
            </Alert>
            <TextField
              fullWidth
              label="Account Code"
              value={formData.account_code}
              disabled
              sx={{ mb: 2 }}
              helperText="Account code cannot be changed"
            />
            <TextField
              fullWidth
              label="Account Name *"
              value={formData.account_name}
              onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
              required
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              multiline
              rows={3}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.value })}
                label="Status"
              >
                <MenuItem value={true}>Active</MenuItem>
                <MenuItem value={false}>Inactive</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseEditDialog}>Cancel</Button>
            <Button onClick={handleSubmit} variant="contained">Update Account</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default ChartOfAccounts;
