import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Snackbar,
  Chip,
} from '@mui/material';
import Layout from '../../components/Layout';
import MoneyOffIcon from '@mui/icons-material/MoneyOff';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';

// Common expense types with their account mappings
const EXPENSE_TYPES = [
  { label: 'Priest Salary', account_code: '5101', category: 'Operational' },
  { label: 'Staff Salary', account_code: '5102', category: 'Operational' },
  { label: 'Electricity Bill', account_code: '5110', category: 'Operational' },
  { label: 'Water Bill', account_code: '5111', category: 'Operational' },
  { label: 'Maintenance & Repairs', account_code: '5120', category: 'Operational' },
  { label: 'Flower Decoration', account_code: '5201', category: 'Pooja & Ritual' },
  { label: 'Pooja Materials', account_code: '5202', category: 'Pooja & Ritual' },
  { label: 'Prasadam Expense', account_code: '5203', category: 'Pooja & Ritual' },
  { label: 'Vegetables & Groceries', account_code: '5301', category: 'Annadana' },
  { label: 'Cooking Gas', account_code: '5302', category: 'Annadana' },
  { label: 'Tent Hiring', account_code: '5401', category: 'Festival' },
  { label: 'Sound System', account_code: '5402', category: 'Festival' },
  { label: 'Lighting Expense', account_code: '5403', category: 'Festival' },
  { label: 'Audit Fees', account_code: '5501', category: 'Administrative' },
  { label: 'Bank Charges', account_code: '5502', category: 'Administrative' },
  { label: 'Printing & Stationery', account_code: '5503', category: 'Administrative' },
];

// Payment methods with their account mappings
const PAYMENT_METHODS = [
  { label: 'Cash - Counter', account_code: '1101' },
  { label: 'Cash - Hundi', account_code: '1102' },
  { label: 'Bank - SBI Current Account', account_code: '1110' },
  { label: 'Bank - HDFC Savings Account', account_code: '1111' },
];

function QuickExpense() {
  const [accounts, setAccounts] = useState([]);
  const [todayExpenses, setTodayExpenses] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Form state
  const [expenseType, setExpenseType] = useState('');
  const [amount, setAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [description, setDescription] = useState('');
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split('T')[0]);
  const [referenceNumber, setReferenceNumber] = useState('');

  useEffect(() => {
    fetchAccounts();
    fetchTodayExpenses();
  }, []);

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/accounts/`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      // Flatten the hierarchical accounts
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

  const fetchTodayExpenses = async () => {
    try {
      const token = localStorage.getItem('token');
      const today = new Date().toISOString().split('T')[0];
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/api/v1/journal-entries/?from_date=${today}&to_date=${today}&reference_type=EXPENSE`,
        {
          headers: { 'Authorization': `Bearer ${token}` },
        }
      );
      const data = await response.json();
      setTodayExpenses(data);
    } catch (error) {
      console.error('Error fetching today expenses:', error);
    }
  };

  const getAccountIdByCode = (code) => {
    const account = accounts.find(acc => acc.account_code === code);
    return account ? account.id : null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!expenseType || !amount || !paymentMethod || !description) {
      setSnackbar({ open: true, message: 'Please fill all required fields', severity: 'error' });
      return;
    }

    const selectedExpense = EXPENSE_TYPES.find(exp => exp.account_code === expenseType);
    const selectedPayment = PAYMENT_METHODS.find(pay => pay.account_code === paymentMethod);

    const expenseAccountId = getAccountIdByCode(expenseType);
    const paymentAccountId = getAccountIdByCode(paymentMethod);

    if (!expenseAccountId || !paymentAccountId) {
      setSnackbar({ open: true, message: 'Invalid account mapping', severity: 'error' });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const payload = {
        entry_date: expenseDate,
        narration: `${selectedExpense.label} - ${description}`,
        reference_type: 'EXPENSE',
        reference_number: referenceNumber || undefined,
        journal_lines: [
          {
            account_id: expenseAccountId,
            debit_amount: parseFloat(amount),
            credit_amount: 0,
            description: description,
          },
          {
            account_id: paymentAccountId,
            debit_amount: 0,
            credit_amount: parseFloat(amount),
            description: `Paid via ${selectedPayment.label}`,
          },
        ],
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
        const data = await response.json();
        setSnackbar({
          open: true,
          message: `Expense recorded successfully! Entry #${data.entry_number}`,
          severity: 'success',
        });
        // Reset form
        setExpenseType('');
        setAmount('');
        setPaymentMethod('');
        setDescription('');
        setReferenceNumber('');
        // Refresh today's expenses
        fetchTodayExpenses();
      } else {
        const error = await response.json();
        setSnackbar({ open: true, message: error.detail || 'Failed to record expense', severity: 'error' });
      }
    } catch (error) {
      console.error('Error recording expense:', error);
      setSnackbar({ open: true, message: 'Error recording expense', severity: 'error' });
    }
  };

  const totalExpensesToday = todayExpenses.reduce((sum, exp) => sum + exp.total_amount, 0);

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <MoneyOffIcon sx={{ fontSize: 40, mr: 2, color: '#d32f2f' }} />
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            Quick Expense Entry
          </Typography>
        </Box>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Card sx={{ bgcolor: '#ffebee' }}>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Total Expenses Today</Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#d32f2f' }}>
                  ₹{totalExpensesToday.toFixed(2)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ bgcolor: '#e3f2fd' }}>
              <CardContent>
                <Typography variant="h6" color="text.secondary">Transactions Today</Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#1976d2' }}>
                  {todayExpenses.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Quick Entry Form */}
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <ReceiptLongIcon sx={{ mr: 1, color: '#d32f2f' }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Record Expense
                </Typography>
              </Box>

              <form onSubmit={handleSubmit}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl fullWidth required>
                      <InputLabel>Expense Type</InputLabel>
                      <Select
                        value={expenseType}
                        onChange={(e) => setExpenseType(e.target.value)}
                        label="Expense Type"
                      >
                        {EXPENSE_TYPES.map((exp) => (
                          <MenuItem key={exp.account_code} value={exp.account_code}>
                            {exp.label} ({exp.category})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      label="Amount"
                      type="number"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                      fullWidth
                      required
                      inputProps={{ step: '0.01', min: '0' }}
                      InputProps={{
                        startAdornment: <Typography sx={{ mr: 1 }}>₹</Typography>,
                      }}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <FormControl fullWidth required>
                      <InputLabel>Payment Method</InputLabel>
                      <Select
                        value={paymentMethod}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                        label="Payment Method"
                      >
                        {PAYMENT_METHODS.map((method) => (
                          <MenuItem key={method.account_code} value={method.account_code}>
                            {method.label}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      label="Description"
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      fullWidth
                      required
                      multiline
                      rows={2}
                      placeholder="E.g., Monthly electricity bill for January"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      label="Expense Date"
                      type="date"
                      value={expenseDate}
                      onChange={(e) => setExpenseDate(e.target.value)}
                      fullWidth
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      label="Reference Number (Optional)"
                      value={referenceNumber}
                      onChange={(e) => setReferenceNumber(e.target.value)}
                      fullWidth
                      placeholder="E.g., Bill No: EB/2025/001"
                    />
                  </Grid>

                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      variant="contained"
                      fullWidth
                      size="large"
                      sx={{ bgcolor: '#d32f2f', '&:hover': { bgcolor: '#b71c1c' } }}
                    >
                      Record Expense
                    </Button>
                  </Grid>
                </Grid>
              </form>
            </Paper>
          </Grid>

          {/* Today's Expenses */}
          <Grid item xs={12} md={7}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                Today's Expenses
              </Typography>

              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ bgcolor: '#d32f2f' }}>
                      <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Entry #</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Narration</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">Amount</TableCell>
                      <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {todayExpenses.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          <Typography color="text.secondary">No expenses recorded today</Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      todayExpenses.map((expense) => (
                        <TableRow key={expense.id} hover>
                          <TableCell>{expense.entry_number}</TableCell>
                          <TableCell>{expense.narration}</TableCell>
                          <TableCell align="right">₹{expense.total_amount.toFixed(2)}</TableCell>
                          <TableCell>
                            <Chip
                              label={expense.status}
                              color={expense.status === 'POSTED' ? 'success' : 'warning'}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>

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

export default QuickExpense;
