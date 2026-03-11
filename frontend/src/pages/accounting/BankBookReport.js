import React, { useState } from 'react';
import {
    Box, Typography, TextField, Button, Grid, Alert,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import { fetchWithApiFallback } from '../../utils/apiBaseUrl';

const BankBookReport = ({ token, accounts }) => {
    const [selectedAccount, setSelectedAccount] = useState('');
    const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]);
    const [toDate, setToDate] = useState(new Date().toISOString().split('T')[0]);
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);

    // Filter accounts to only show bank/cash types
    const bankAccounts = (accounts || []).filter(a => a.account_code?.startsWith('11') || a.account_subtype === 'CASH_BANK');

    const fetchBankBook = async () => {
        if (!selectedAccount) {
            alert('Please select a bank account');
            return;
        }
        setLoading(true);
        try {
            const response = await fetchWithApiFallback(`/api/v1/journal-entries/reports/bank-book/${selectedAccount}?from_date=${fromDate}&to_date=${toDate}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await response.json();
            setReport(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box>
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                    <FormControl fullWidth>
                        <InputLabel>Select Bank Account</InputLabel>
                        <Select
                            value={selectedAccount}
                            onChange={(e) => setSelectedAccount(e.target.value)}
                            label="Select Bank Account"
                        >
                            {bankAccounts.map((account) => (
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
                        value={fromDate}
                        onChange={(e) => setFromDate(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <TextField
                        label="To Date"
                        type="date"
                        value={toDate}
                        onChange={(e) => setToDate(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>
                <Grid item xs={12} md={3}>
                    <Button
                        variant="contained"
                        onClick={fetchBankBook}
                        disabled={loading || !selectedAccount}
                        fullWidth
                        sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                    >
                        {loading ? 'Loading...' : 'Generate Bank Book'}
                    </Button>
                </Grid>
            </Grid>

            {report && (
                <Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                        Bank Book for {report.account_code} - {report.account_name} ({report.bank_name || 'N/A'})
                        <Typography variant="body2" sx={{ mt: 1 }}>Period: {new Date(report.from_date).toLocaleDateString()} to {new Date(report.to_date).toLocaleDateString()}</Typography>
                    </Alert>

                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Entry #</TableCell>
                                    <TableCell>Narration</TableCell>
                                    <TableCell>Cheque/Ref No.</TableCell>
                                    <TableCell align="right">Deposit (₹)</TableCell>
                                    <TableCell align="right">Withdrawal (₹)</TableCell>
                                    <TableCell align="right">Balance (₹)</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                                    <TableCell colSpan={6}><strong>Opening Balance</strong></TableCell>
                                    <TableCell align="right"><strong>₹{(report.opening_balance || 0).toFixed(2)}</strong></TableCell>
                                </TableRow>
                                {report.entries && report.entries.length > 0 ? (
                                    report.entries.map((entry, i) => (
                                        <TableRow key={i}>
                                            <TableCell>{new Date(entry.date).toLocaleDateString()}</TableCell>
                                            <TableCell>{entry.entry_number}</TableCell>
                                            <TableCell>{entry.narration} {!entry.cleared && <Box component="span" sx={{ ml: 1, fontSize: '0.7rem', bgcolor: 'warning.light', px: 1, borderRadius: 1 }}>Pending</Box>}</TableCell>
                                            <TableCell>{entry.cheque_number || '-'}</TableCell>
                                            <TableCell align="right">{entry.deposit_amount > 0 ? entry.deposit_amount.toFixed(2) : '-'}</TableCell>
                                            <TableCell align="right">{entry.withdrawal_amount > 0 ? entry.withdrawal_amount.toFixed(2) : '-'}</TableCell>
                                            <TableCell align="right">₹{entry.running_balance.toFixed(2)}</TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow><TableCell colSpan={7} align="center">No bank transactions in this period</TableCell></TableRow>
                                )}
                                <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                                    <TableCell colSpan={4}><strong>Total</strong></TableCell>
                                    <TableCell align="right"><strong>₹{(report.total_deposits || 0).toFixed(2)}</strong></TableCell>
                                    <TableCell align="right"><strong>₹{(report.total_withdrawals || 0).toFixed(2)}</strong></TableCell>
                                    <TableCell align="right"><strong>Closing: ₹{(report.closing_balance || 0).toFixed(2)}</strong></TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>
            )}
        </Box>
    );
};

export default BankBookReport;
