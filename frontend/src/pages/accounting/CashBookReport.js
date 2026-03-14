import React, { useState } from 'react';
import {
    Box, TextField, Button, Grid, Alert,
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import { fetchWithApiFallback } from '../../utils/apiBaseUrl';

const CashBookReport = ({ token }) => {
    const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]);
    const [toDate, setToDate] = useState(new Date().toISOString().split('T')[0]);
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchCashBook = async () => {
        setLoading(true);
        try {
            const response = await fetchWithApiFallback(`/api/v1/journal-entries/reports/cash-book?from_date=${fromDate}&to_date=${toDate}`, {
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
                        label="From Date"
                        type="date"
                        value={fromDate}
                        onChange={(e) => setFromDate(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <TextField
                        label="To Date"
                        type="date"
                        value={toDate}
                        onChange={(e) => setToDate(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                    />
                </Grid>
                <Grid item xs={12} md={4}>
                    <Button
                        variant="contained"
                        onClick={fetchCashBook}
                        disabled={loading}
                        fullWidth
                        sx={{ height: 56, bgcolor: '#FF9933', '&:hover': { bgcolor: '#E68A2E' } }}
                    >
                        {loading ? 'Loading...' : 'Generate Cash Book'}
                    </Button>
                </Grid>
            </Grid>

            {report && (
                <Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                        Cash Book from {new Date(report.from_date).toLocaleDateString()} to {new Date(report.to_date).toLocaleDateString()}
                    </Alert>

                    <TableContainer>
                        <Table size="small">
                            <TableHead>
                                <TableRow sx={{ bgcolor: '#f5f5f5' }}>
                                    <TableCell>Date</TableCell>
                                    <TableCell>Entry #</TableCell>
                                    <TableCell>Narration</TableCell>
                                    <TableCell align="right">Receipt (â‚¹)</TableCell>
                                    <TableCell align="right">Payment (â‚¹)</TableCell>
                                    <TableCell align="right">Balance (â‚¹)</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                                    <TableCell colSpan={5}><strong>Opening Balance</strong></TableCell>
                                    <TableCell align="right"><strong>â‚¹{(report.opening_balance || 0).toFixed(2)}</strong></TableCell>
                                </TableRow>
                                {report.entries && report.entries.length > 0 ? (
                                    report.entries.map((entry, i) => (
                                        <TableRow key={i}>
                                            <TableCell>{new Date(entry.date).toLocaleDateString()}</TableCell>
                                            <TableCell>{entry.entry_number}</TableCell>
                                            <TableCell>{entry.narration}</TableCell>
                                            <TableCell align="right">{entry.receipt_amount > 0 ? entry.receipt_amount.toFixed(2) : '-'}</TableCell>
                                            <TableCell align="right">{entry.payment_amount > 0 ? entry.payment_amount.toFixed(2) : '-'}</TableCell>
                                            <TableCell align="right">â‚¹{entry.running_balance.toFixed(2)}</TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow><TableCell colSpan={6} align="center">No cash transactions in this period</TableCell></TableRow>
                                )}
                                <TableRow sx={{ bgcolor: '#FFF3E0' }}>
                                    <TableCell colSpan={3}><strong>Total</strong></TableCell>
                                    <TableCell align="right"><strong>â‚¹{(report.total_receipts || 0).toFixed(2)}</strong></TableCell>
                                    <TableCell align="right"><strong>â‚¹{(report.total_payments || 0).toFixed(2)}</strong></TableCell>
                                    <TableCell align="right"><strong>Closing: â‚¹{(report.closing_balance || 0).toFixed(2)}</strong></TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </TableContainer>
                </Box>
            )}
        </Box>
    );
};

export default CashBookReport;
