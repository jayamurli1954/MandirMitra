import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Button,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    TextField,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    IconButton,
    Alert,
    CircularProgress,
    Divider,
    Stepper,
    Step,
    StepLabel,
} from '@mui/material';
import Layout from '../../components/Layout';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';

const BankReconciliation = () => {
    const { showSuccess, showError } = useNotification();
    const [activeStep, setActiveStep] = useState(0);
    const [bankAccounts, setBankAccounts] = useState([]);
    const [selectedAccount, setSelectedAccount] = useState('');
    const [file, setFile] = useState(null);
    const [statementDate, setStatementDate] = useState(new Date().toISOString().split('T')[0]);
    const [loading, setLoading] = useState(false);
    const [statement, setStatement] = useState(null);
    const [summary, setSummary] = useState(null);
    const [statementEntries, setStatementEntries] = useState([]);
    const [bookEntries, setBookEntries] = useState([]);
    const [matchingItem, setMatchingItem] = useState(null); // Current statement entry being matched

    useEffect(() => {
        fetchBankAccounts();
    }, []);

    const fetchBankAccounts = async () => {
        try {
            const response = await api.get('/api/v1/bank-reconciliation/accounts');
            setBankAccounts(response.data);
        } catch (err) {
            showError('Failed to fetch bank accounts');
        }
    };

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    };

    const handleImport = async () => {
        if (!selectedAccount || !file || !statementDate) {
            showError('Please select account, date and file');
            return;
        }

        setLoading(true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await api.post(
                `/api/v1/bank-reconciliation/statements/import?account_id=${selectedAccount}&statement_date=${statementDate}`,
                formData,
                {
                    headers: { 'Content-Type': 'multipart/form-data' },
                }
            );

            setStatement(response.data);
            showSuccess('Bank statement imported successfully');
            fetchReconciliationData(response.data.id);
            setActiveStep(1);
        } catch (err) {
            showError(err.response?.data?.detail || 'Failed to import statement');
        } finally {
            setLoading(false);
        }
    };

    const fetchReconciliationData = async (statementId) => {
        setLoading(true);
        try {
            const [summaryRes, entriesRes, bookRes] = await Promise.all([
                api.get(`/api/v1/bank-reconciliation/statements/${statementId}/summary`),
                api.get(`/api/v1/bank-reconciliation/statements/${statementId}/entries`),
                api.get(`/api/v1/bank-reconciliation/statements/${statementId}/unmatched-book-entries`)
            ]);

            setSummary(summaryRes.data);
            setStatementEntries(entriesRes.data);
            setBookEntries(bookRes.data);
        } catch (err) {
            showError('Failed to fetch reconciliation details');
        } finally {
            setLoading(false);
        }
    };

    const handleMatch = async (statementEntryId, journalLineId) => {
        try {
            await api.post('/api/v1/bank-reconciliation/match', {
                statement_entry_id: statementEntryId,
                journal_line_id: journalLineId
            });
            showSuccess('Entry matched successfully');
            setMatchingItem(null);
            fetchReconciliationData(statement.id);
        } catch (err) {
            showError(err.response?.data?.detail || 'Matching failed');
        }
    };

    const handleFinalReconcile = async () => {
        setLoading(true);
        try {
            await api.post('/api/v1/bank-reconciliation/reconcile', {
                account_id: selectedAccount,
                statement_id: statement.id,
                reconciliation_date: statementDate,
                notes: 'Final reconciliation'
            });
            showSuccess('Bank reconciliation completed successfully');
            setActiveStep(2);
        } catch (err) {
            showError(err.response?.data?.detail || 'Reconciliation failed');
        } finally {
            setLoading(false);
        }
    };

    const renderStep0 = () => (
        <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
            <Typography variant="h6" gutterBottom>Import Bank Statement</Typography>
            <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 3 }}>
                <FormControl fullWidth>
                    <InputLabel>Bank Account</InputLabel>
                    <Select
                        value={selectedAccount}
                        onChange={(e) => setSelectedAccount(e.target.value)}
                        label="Bank Account"
                    >
                        {bankAccounts.map((acc) => (
                            <MenuItem key={acc.id} value={acc.id}>{acc.code} - {acc.name}</MenuItem>
                        ))}
                    </Select>
                </FormControl>

                <TextField
                    label="Statement Date"
                    type="date"
                    value={statementDate}
                    onChange={(e) => setStatementDate(e.target.value)}
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                />

                <Box sx={{ border: '2px dashed #ccc', p: 3, textAlign: 'center', borderRadius: 2 }}>
                    <input
                        accept=".csv"
                        style={{ display: 'none' }}
                        id="raised-button-file"
                        type="file"
                        onChange={handleFileChange}
                    />
                    <label htmlFor="raised-button-file">
                        <Button variant="outlined" component="span" startIcon={<CloudUploadIcon />} sx={{ mb: 1 }}>
                            Select CSV File
                        </Button>
                    </label>
                    <Typography variant="body2" color="textSecondary">
                        {file ? file.name : 'Expected format: Date, Description, Debit, Credit, Balance'}
                    </Typography>
                </Box>

                <Button
                    variant="contained"
                    color="primary"
                    size="large"
                    onClick={handleImport}
                    disabled={loading || !file || !selectedAccount}
                    sx={{ py: 1.5 }}
                >
                    {loading ? <CircularProgress size={24} color="inherit" /> : 'Import & Continue'}
                </Button>
            </Box>
        </Paper>
    );

    const renderStep1 = () => (
        <Box sx={{ mt: 3 }}>
            {summary && (
                <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e3f2fd' }}>
                            <Typography variant="caption" color="textSecondary">Statement Balance</Typography>
                            <Typography variant="h6">₹{summary.statement_balance?.toLocaleString()}</Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#fff3e0' }}>
                            <Typography variant="caption" color="textSecondary">Book Balance</Typography>
                            <Typography variant="h6">₹{summary.book_balance?.toLocaleString()}</Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: summary.difference === 0 ? '#e8f5e9' : '#ffebee' }}>
                            <Typography variant="caption" color="textSecondary">Difference</Typography>
                            <Typography variant="h6">₹{summary.difference?.toLocaleString()}</Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                        <Box sx={{ display: 'flex', gap: 1, height: '100%', alignItems: 'center' }}>
                            <Button
                                variant="contained"
                                color="success"
                                fullWidth
                                onClick={handleFinalReconcile}
                                disabled={summary.difference !== 0 || loading}
                                startIcon={<CheckCircleIcon />}
                            >
                                Finalize
                            </Button>
                        </Box>
                    </Grid>
                </Grid>
            )}

            <Grid container spacing={2}>
                {/* Bank Statement Side */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 0 }}>
                        <Box sx={{ p: 2, bgcolor: '#f5f5f5', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="subtitle1" fontWeight="bold">Bank Statement Entries</Typography>
                            <Chip label={`Unmatched: ${statementEntries.filter(e => !e.is_matched).length}`} size="small" color="primary" />
                        </Box>
                        <TableContainer sx={{ maxHeight: 500 }}>
                            <Table stickyHeader size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Date</TableCell>
                                        <TableCell>Description</TableCell>
                                        <TableCell align="right">Amount</TableCell>
                                        <TableCell align="center">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {statementEntries.map((entry) => (
                                        <TableRow key={entry.id} sx={{ bgcolor: entry.is_matched ? '#e8f5e9' : 'inherit' }}>
                                            <TableCell>{new Date(entry.transaction_date).toLocaleDateString()}</TableCell>
                                            <TableCell sx={{ fontSize: '0.8rem' }}>{entry.description}</TableCell>
                                            <TableCell align="right" sx={{ color: entry.amount >= 0 ? 'success.main' : 'error.main' }}>
                                                ₹{Math.abs(entry.amount).toLocaleString()}
                                            </TableCell>
                                            <TableCell align="center">
                                                {entry.is_matched ? (
                                                    <CheckCircleIcon color="success" fontSize="small" />
                                                ) : (
                                                    <Button
                                                        size="small"
                                                        variant={matchingItem?.id === entry.id ? "contained" : "outlined"}
                                                        onClick={() => setMatchingItem(entry)}
                                                    >
                                                        Match
                                                    </Button>
                                                )}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>

                {/* Book Entries Side */}
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 0 }}>
                        <Box sx={{ p: 2, bgcolor: '#f5f5f5', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="subtitle1" fontWeight="bold">Book Entries (Journal Lines)</Typography>
                            {matchingItem && (
                                <Chip
                                    label={`Matching: ₹${Math.abs(matchingItem.amount).toLocaleString()}`}
                                    color="warning"
                                    onDelete={() => setMatchingItem(null)}
                                    size="small"
                                />
                            )}
                        </Box>
                        <TableContainer sx={{ maxHeight: 500 }}>
                            <Table stickyHeader size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Date</TableCell>
                                        <TableCell>Narration</TableCell>
                                        <TableCell align="right">Amount</TableCell>
                                        <TableCell align="center">Action</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {bookEntries.map((line) => (
                                        <TableRow key={line.id}>
                                            <TableCell>{new Date(line.entry_date).toLocaleDateString()}</TableCell>
                                            <TableCell sx={{ fontSize: '0.8rem' }}>{line.narration}</TableCell>
                                            <TableCell align="right">₹{line.amount.toLocaleString()}</TableCell>
                                            <TableCell align="center">
                                                <Button
                                                    size="small"
                                                    variant="contained"
                                                    color="secondary"
                                                    disabled={!matchingItem || Math.abs(Math.abs(matchingItem.amount) - line.amount) > 0.01}
                                                    onClick={() => handleMatch(matchingItem.id, line.id)}
                                                >
                                                    Select
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );

    const renderStep2 = () => (
        <Paper sx={{ p: 6, textAlign: 'center', mt: 4 }}>
            <CheckCircleIcon sx={{ fontSize: 100, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom>Success!</Typography>
            <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
                The bank account has been reconciled with the statement.
                A reconciliation record has been created for your audits.
            </Typography>
            <Button variant="contained" onClick={() => setActiveStep(0)}>Next Statement</Button>
        </Paper>
    );

    return (
        <Layout>
            <Box sx={{ p: 3 }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                    Bank Reconciliation
                </Typography>

                <Stepper activeStep={activeStep} sx={{ mb: 4, mt: 3 }}>
                    <Step><StepLabel>Import Statement</StepLabel></Step>
                    <Step><StepLabel>Match Transactions</StepLabel></Step>
                    <Step><StepLabel>Complete</StepLabel></Step>
                </Stepper>

                {activeStep === 0 && renderStep0()}
                {activeStep === 1 && renderStep1()}
                {activeStep === 2 && renderStep2()}
            </Box>
        </Layout>
    );
};

export default BankReconciliation;
