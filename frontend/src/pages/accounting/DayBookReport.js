import React, { useState } from 'react';
import {
    Box, Typography, TextField, Button, Grid, Alert,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import { fetchWithApiFallback } from '../../utils/apiBaseUrl';

const DayBookReport = ({ token }) => {
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchDayBook = async () => {
        setLoading(true);
        try {
            const response = await fetchWithApiFallback(`/api/v1/journal-entries/reports/day-book?date=${date}`, {
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
                <Grid item xs={12} md={4}>
                    <TextField
                        label="Date"
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <Button
                        variant="contained"
                        onClick={fetchDayBook}
                        disabled={loading}
                        sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                    >
                        {loading ? 'Loading...' : 'Generate Day Book'}
                    </Button>
                </Grid>
            </Grid>

            {report && (
                <Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                        Day Book for {new Date(report.date).toLocaleDateString()}
                        <Typography variant="body2" sx={{ mt: 1 }}>Opening Balance: ₹{report.opening_balance.toFixed(2)}</Typography>
                        <Typography variant="body2">Closing Balance: ₹{report.closing_balance.toFixed(2)}</Typography>
                    </Alert>

                    <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>Receipts (Cash IN)</Typography>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                                    <TableCell>Entry #</TableCell>
                                    <TableCell>Account</TableCell>
                                    <TableCell>Narration</TableCell>
                                    <TableCell align="right">Amount (₹)</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {report.receipts && report.receipts.length > 0 ? (
                                    report.receipts.map((r, i) => (
                                        <TableRow key={i}>
                                            <TableCell>{r.entry_number}</TableCell>
                                            <TableCell>{r.account_name}</TableCell>
                                            <TableCell>{r.narration}</TableCell>
                                            <TableCell align="right">₹{r.debit_amount.toFixed(2)}</TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow><TableCell colSpan={4} align="center">No receipts</TableCell></TableRow>
                                )}
                                <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                                    <TableCell colSpan={3}><strong>Total Receipts</strong></TableCell>
                                    <TableCell align="right"><strong>₹{(report.total_receipts || 0).toFixed(2)}</strong></TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </TableContainer>

                    <Typography variant="h6" sx={{ mt: 4, mb: 1 }}>Payments (Cash OUT)</Typography>
                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                                    <TableCell>Entry #</TableCell>
                                    <TableCell>Account</TableCell>
                                    <TableCell>Narration</TableCell>
                                    <TableCell align="right">Amount (₹)</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {report.payments && report.payments.length > 0 ? (
                                    report.payments.map((p, i) => (
                                        <TableRow key={i}>
                                            <TableCell>{p.entry_number}</TableCell>
                                            <TableCell>{p.account_name}</TableCell>
                                            <TableCell>{p.narration}</TableCell>
                                            <TableCell align="right">₹{p.credit_amount.toFixed(2)}</TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow><TableCell colSpan={4} align="center">No payments</TableCell></TableRow>
                                )}
                                <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                                    <TableCell colSpan={3}><strong>Total Payments</strong></TableCell>
                                    <TableCell align="right"><strong>₹{(report.total_payments || 0).toFixed(2)}</strong></TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>
            )}
        </Box>
    );
};

export default DayBookReport;
