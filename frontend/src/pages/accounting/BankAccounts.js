import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  FormControlLabel,
  Checkbox,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import Layout from '../../components/Layout';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

function BankAccounts() {
  const { showSuccess, showError } = useNotification();
  const [bankAccounts, setBankAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [formData, setFormData] = useState({
    account_name: '',
    bank_name: '',
    branch_name: '',
    account_number: '',
    ifsc_code: '',
    account_type: 'Savings',
    is_primary: false,
    is_active: true,
  });

  useEffect(() => {
    fetchBankAccounts();
  }, []);

  const fetchBankAccounts = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/bank-accounts');
      setBankAccounts(response.data || []);
    } catch (err) {
      showError(err.response?.data?.detail || 'Error fetching bank accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (account = null) => {
    if (account) {
      setEditingAccount(account);
      setFormData({
        account_name: account.account_name || '',
        bank_name: account.bank_name || '',
        branch_name: account.branch_name || '',
        account_number: account.account_number || '',
        ifsc_code: account.ifsc_code || '',
        account_type: account.account_type || 'Savings',
        is_primary: account.is_primary || false,
        is_active: account.is_active !== undefined ? account.is_active : true,
      });
    } else {
      setEditingAccount(null);
      setFormData({
        account_name: '',
        bank_name: '',
        branch_name: '',
        account_number: '',
        ifsc_code: '',
        account_type: 'Savings',
        is_primary: false,
        is_active: true,
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingAccount(null);
    setFormData({
      account_name: '',
      bank_name: '',
      branch_name: '',
      account_number: '',
      ifsc_code: '',
      account_type: 'Savings',
      is_primary: false,
      is_active: true,
    });
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.account_name || !formData.bank_name || !formData.account_number || !formData.ifsc_code) {
      showError('Please fill all required fields');
      return;
    }

    // IFSC code validation (should be 11 characters: 4 letters + 0 + 6 alphanumeric)
    if (formData.ifsc_code.length !== 11) {
      showError('IFSC code must be 11 characters (e.g., SBIN0001234)');
      return;
    }

    try {
      if (editingAccount) {
        // Update existing account
        await api.put(`/api/v1/bank-accounts/${editingAccount.id}`, formData);
        showSuccess('Bank account updated successfully');
      } else {
        // Create new account
        await api.post('/api/v1/bank-accounts', formData);
        showSuccess('Bank account added successfully');
      }
      handleCloseDialog();
      fetchBankAccounts();
    } catch (err) {
      showError(err.response?.data?.detail || 'Error saving bank account');
    }
  };

  const handleDelete = async (accountId) => {
    if (!window.confirm('Are you sure you want to delete this bank account? This will mark it as inactive.')) {
      return;
    }

    try {
      await api.delete(`/api/v1/bank-accounts/${accountId}`);
      showSuccess('Bank account deleted successfully');
      fetchBankAccounts();
    } catch (err) {
      showError(err.response?.data?.detail || 'Error deleting bank account');
    }
  };

  const maskAccountNumber = (accountNumber) => {
    if (!accountNumber || accountNumber.length < 4) return accountNumber;
    return `****${accountNumber.slice(-4)}`;
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccountBalanceIcon sx={{ fontSize: 40, mr: 2, color: '#1976d2' }} />
            <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
              Bank Account Management
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            sx={{ bgcolor: '#1976d2' }}
          >
            Add Bank Account
          </Button>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Multiple Bank Accounts:</strong> You can add multiple bank accounts for your temple. 
            Mark one as "Primary" to use it as the default for online payments (Card, UPI, Online, Cheque).
            When recording donations with non-cash payment modes, you'll be able to select which bank account received the payment.
          </Typography>
        </Alert>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : bankAccounts.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No bank accounts configured
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Add your first bank account to start recording online payments
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Add Bank Account
            </Button>
          </Paper>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead sx={{ bgcolor: '#f5f5f5' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Account Name</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Bank Name</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Branch</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Account Number</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>IFSC Code</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Type</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {bankAccounts.map((account) => (
                  <TableRow key={account.id} hover>
                    <TableCell>
                      {account.account_name}
                      {account.is_primary && (
                        <Chip
                          label="Primary"
                          size="small"
                          color="primary"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </TableCell>
                    <TableCell>{account.bank_name}</TableCell>
                    <TableCell>{account.branch_name || 'N/A'}</TableCell>
                    <TableCell>{maskAccountNumber(account.account_number)}</TableCell>
                    <TableCell>{account.ifsc_code}</TableCell>
                    <TableCell>{account.account_type || 'Savings'}</TableCell>
                    <TableCell>
                      <Chip
                        label={account.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={account.is_active ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(account)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(account.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {/* Add/Edit Dialog */}
        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>
            {editingAccount ? 'Edit Bank Account' : 'Add New Bank Account'}
          </DialogTitle>
          <form onSubmit={handleSubmit}>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Account Name *"
                    name="account_name"
                    value={formData.account_name}
                    onChange={handleChange}
                    required
                    helperText="e.g., SBI Current Account, HDFC Savings"
                    placeholder="SBI Current Account"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Bank Name *"
                    name="bank_name"
                    value={formData.bank_name}
                    onChange={handleChange}
                    required
                    helperText="e.g., State Bank of India, HDFC Bank"
                    placeholder="State Bank of India"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Branch Name"
                    name="branch_name"
                    value={formData.branch_name}
                    onChange={handleChange}
                    helperText="Optional: Branch location"
                    placeholder="Main Branch, Bangalore"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Account Number *"
                    name="account_number"
                    value={formData.account_number}
                    onChange={handleChange}
                    required
                    helperText="Full account number"
                    inputProps={{ maxLength: 50 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="IFSC Code *"
                    name="ifsc_code"
                    value={formData.ifsc_code}
                    onChange={handleChange}
                    required
                    helperText="11 characters (e.g., SBIN0001234)"
                    placeholder="SBIN0001234"
                    inputProps={{ maxLength: 11, style: { textTransform: 'uppercase' } }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Account Type *"
                    name="account_type"
                    value={formData.account_type}
                    onChange={handleChange}
                    required
                  >
                    <MenuItem value="Savings">Savings</MenuItem>
                    <MenuItem value="Current">Current</MenuItem>
                    <MenuItem value="Fixed Deposit">Fixed Deposit</MenuItem>
                    <MenuItem value="Recurring Deposit">Recurring Deposit</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.is_primary}
                        onChange={handleChange}
                        name="is_primary"
                      />
                    }
                    label="Set as Primary Account (Default for online payments)"
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', ml: 4 }}>
                    Only one account can be primary. Setting this will unset the current primary account.
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={formData.is_active}
                        onChange={handleChange}
                        name="is_active"
                      />
                    }
                    label="Active"
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', ml: 4 }}>
                    Inactive accounts won't appear in payment dropdowns
                  </Typography>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Cancel</Button>
              <Button type="submit" variant="contained" color="primary">
                {editingAccount ? 'Update' : 'Add'} Bank Account
              </Button>
            </DialogActions>
          </form>
        </Dialog>
      </Box>
    </Layout>
  );
}

export default BankAccounts;

