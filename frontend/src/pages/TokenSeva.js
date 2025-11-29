import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Autocomplete,
  Stack,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import InventoryIcon from '@mui/icons-material/Inventory';
import PointOfSaleIcon from '@mui/icons-material/PointOfSale';
import QueueIcon from '@mui/icons-material/Queue';
import AssessmentIcon from '@mui/icons-material/Assessment';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

function TokenSeva() {
  const { showSuccess, showError } = useNotification();
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sevas, setSevas] = useState([]);
  const [selectedSeva, setSelectedSeva] = useState(null);
  
  // Inventory state
  const [inventory, setInventory] = useState([]);
  const [inventoryStatus, setInventoryStatus] = useState([]);
  const [addInventoryOpen, setAddInventoryOpen] = useState(false);
  const [inventoryForm, setInventoryForm] = useState({
    seva_id: '',
    token_color: '',
    serial_number: '',
    token_number: '',
    batch_number: '',
    printed_date: '',
    expiry_date: '',
  });
  
  // Sale state
  const [sales, setSales] = useState([]);
  const [saleForm, setSaleForm] = useState({
    seva_id: '',
    token_serial_number: '',
    amount: '',
    payment_mode: 'cash',
    upi_reference: '',
    counter_number: '',
    devotee_id: null,
    devotee_name: '',
    devotee_phone: '',
    notes: '',
  });
  const [availableTokens, setAvailableTokens] = useState([]);
  const [devotees, setDevotees] = useState([]);
  
  // Reconciliation state
  const [reconciliations, setReconciliations] = useState([]);
  const [reconciliationDate, setReconciliationDate] = useState(new Date().toISOString().split('T')[0]);
  const [reconciliationData, setReconciliationData] = useState(null);
  
  // Queue state
  const [queue, setQueue] = useState([]);

  useEffect(() => {
    loadSevas();
    if (tabValue === 0) loadInventoryStatus();
    if (tabValue === 1) loadSales();
    if (tabValue === 2) loadQueue();
    if (tabValue === 3) loadReconciliations();
  }, [tabValue]);

  const loadSevas = async () => {
    try {
      const response = await api.get('/api/v1/sevas/');
      const tokenSevas = response.data.filter(s => s.is_token_seva);
      setSevas(tokenSevas);
    } catch (error) {
      showError('Failed to load sevas');
    }
  };

  const loadInventoryStatus = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/token-seva/inventory/status');
      setInventoryStatus(response.data);
    } catch (error) {
      showError('Failed to load inventory status');
    } finally {
      setLoading(false);
    }
  };

  const loadSales = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/token-seva/sales');
      setSales(response.data);
    } catch (error) {
      showError('Failed to load sales');
    } finally {
      setLoading(false);
    }
  };

  const loadQueue = async () => {
    setLoading(true);
    try {
      // Load recent sales as queue
      const response = await api.get('/api/v1/token-seva/sales', {
        params: {
          start_date: new Date().toISOString().split('T')[0],
        },
      });
      setQueue(response.data);
    } catch (error) {
      showError('Failed to load queue');
    } finally {
      setLoading(false);
    }
  };

  const loadReconciliations = async () => {
    setLoading(true);
    try {
      // Load reconciliation for today
      const today = new Date().toISOString().split('T')[0];
      try {
        const response = await api.get(`/api/v1/token-seva/reconcile/${today}`);
        setReconciliationData(response.data);
      } catch (error) {
        // No reconciliation for today yet
        setReconciliationData(null);
      }
    } catch (error) {
      showError('Failed to load reconciliation');
    } finally {
      setLoading(false);
    }
  };

  const handleAddInventory = async () => {
    if (!inventoryForm.seva_id || !inventoryForm.serial_number || !inventoryForm.token_number) {
      showError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v1/token-seva/inventory/add', [inventoryForm]);
      showSuccess('Token added to inventory');
      setAddInventoryOpen(false);
      setInventoryForm({
        seva_id: '',
        token_color: '',
        serial_number: '',
        token_number: '',
        batch_number: '',
        printed_date: '',
        expiry_date: '',
      });
      loadInventoryStatus();
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to add token');
    } finally {
      setLoading(false);
    }
  };

  const handleSale = async () => {
    if (!saleForm.seva_id || !saleForm.token_serial_number || !saleForm.amount) {
      showError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v1/token-seva/sale', saleForm);
      showSuccess('Token sale recorded successfully');
      setSaleForm({
        seva_id: '',
        token_serial_number: '',
        amount: '',
        payment_mode: 'cash',
        upi_reference: '',
        counter_number: '',
        devotee_id: null,
        devotee_name: '',
        devotee_phone: '',
        notes: '',
      });
      loadSales();
      loadQueue();
      loadInventoryStatus();
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to record sale');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateReconciliation = async () => {
    setLoading(true);
    try {
      await api.post('/api/v1/token-seva/reconcile', {
        reconciliation_date: reconciliationDate,
      });
      showSuccess('Reconciliation created successfully');
      loadReconciliations();
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to create reconciliation');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveReconciliation = async (reconciliationId) => {
    setLoading(true);
    try {
      await api.put(`/api/v1/token-seva/reconcile/${reconciliationId}/approve`);
      showSuccess('Reconciliation approved');
      loadReconciliations();
    } catch (error) {
      showError(error.response?.data?.detail || 'Failed to approve reconciliation');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableTokens = async (sevaId) => {
    if (!sevaId) return;
    try {
      const response = await api.get('/api/v1/token-seva/inventory/status', {
        params: { seva_id: sevaId },
      });
      // Get available tokens count
      const sevaData = response.data.find(s => s.seva_id === sevaId);
      if (sevaData && sevaData.statuses?.available) {
        // In a real implementation, you'd fetch actual token serial numbers
        setAvailableTokens([]);
      }
    } catch (error) {
      console.error('Failed to load available tokens');
    }
  };

  const loadDevotees = async (searchTerm) => {
    if (!searchTerm || searchTerm.length < 2) return;
    try {
      const response = await api.get('/api/v1/devotees/', {
        params: { search: searchTerm },
      });
      setDevotees(response.data);
    } catch (error) {
      console.error('Failed to load devotees');
    }
  };

  const renderInventoryTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Token Inventory</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setAddInventoryOpen(true)}
        >
          Add Tokens
        </Button>
      </Box>

      <Grid container spacing={3}>
        {inventoryStatus.map((status) => (
          <Grid item xs={12} md={6} lg={4} key={status.seva_id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      bgcolor: status.token_color || '#ccc',
                      mr: 2,
                    }}
                  />
                  <Box>
                    <Typography variant="h6">{status.seva_name}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Seva ID: {status.seva_id}
                    </Typography>
                  </Box>
                </Box>
                <Stack spacing={1}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Available:</Typography>
                    <Chip
                      label={status.statuses?.available || 0}
                      color="success"
                      size="small"
                    />
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Sold:</Typography>
                    <Chip
                      label={status.statuses?.sold || 0}
                      color="primary"
                      size="small"
                    />
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Used:</Typography>
                    <Chip
                      label={status.statuses?.used || 0}
                      color="info"
                      size="small"
                    />
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={addInventoryOpen} onClose={() => setAddInventoryOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Token to Inventory</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              select
              label="Seva"
              value={inventoryForm.seva_id}
              onChange={(e) => {
                const seva = sevas.find(s => s.id === parseInt(e.target.value));
                setInventoryForm({
                  ...inventoryForm,
                  seva_id: e.target.value,
                  token_color: seva?.token_color || '',
                });
              }}
              fullWidth
              required
            >
              {sevas.map((seva) => (
                <MenuItem key={seva.id} value={seva.id}>
                  {seva.name_english}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Token Color"
              value={inventoryForm.token_color}
              onChange={(e) => setInventoryForm({ ...inventoryForm, token_color: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Serial Number"
              value={inventoryForm.serial_number}
              onChange={(e) => setInventoryForm({ ...inventoryForm, serial_number: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Token Number"
              value={inventoryForm.token_number}
              onChange={(e) => setInventoryForm({ ...inventoryForm, token_number: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Batch Number"
              value={inventoryForm.batch_number}
              onChange={(e) => setInventoryForm({ ...inventoryForm, batch_number: e.target.value })}
              fullWidth
            />
            <TextField
              label="Printed Date"
              type="date"
              value={inventoryForm.printed_date}
              onChange={(e) => setInventoryForm({ ...inventoryForm, printed_date: e.target.value })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Expiry Date"
              type="date"
              value={inventoryForm.expiry_date}
              onChange={(e) => setInventoryForm({ ...inventoryForm, expiry_date: e.target.value })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddInventoryOpen(false)}>Cancel</Button>
          <Button onClick={handleAddInventory} variant="contained" disabled={loading}>
            Add Token
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderSaleTab = () => (
    <Box>
      <Typography variant="h5" mb={3}>Token Sale</Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>New Sale</Typography>
            <Stack spacing={2}>
              <TextField
                select
                label="Seva"
                value={saleForm.seva_id}
                onChange={(e) => {
                  setSaleForm({ ...saleForm, seva_id: e.target.value });
                  loadAvailableTokens(parseInt(e.target.value));
                }}
                fullWidth
                required
              >
                {sevas.map((seva) => (
                  <MenuItem key={seva.id} value={seva.id}>
                    {seva.name_english} - ₹{seva.amount}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Token Serial Number"
                value={saleForm.token_serial_number}
                onChange={(e) => setSaleForm({ ...saleForm, token_serial_number: e.target.value })}
                fullWidth
                required
                placeholder="Enter token serial number"
              />
              <TextField
                label="Amount"
                type="number"
                value={saleForm.amount}
                onChange={(e) => setSaleForm({ ...saleForm, amount: e.target.value })}
                fullWidth
                required
              />
              <TextField
                select
                label="Payment Mode"
                value={saleForm.payment_mode}
                onChange={(e) => setSaleForm({ ...saleForm, payment_mode: e.target.value })}
                fullWidth
                required
              >
                <MenuItem value="cash">Cash</MenuItem>
                <MenuItem value="upi">UPI</MenuItem>
              </TextField>
              {saleForm.payment_mode === 'upi' && (
                <TextField
                  label="UPI Reference"
                  value={saleForm.upi_reference}
                  onChange={(e) => setSaleForm({ ...saleForm, upi_reference: e.target.value })}
                  fullWidth
                />
              )}
              <TextField
                label="Counter Number"
                value={saleForm.counter_number}
                onChange={(e) => setSaleForm({ ...saleForm, counter_number: e.target.value })}
                fullWidth
              />
              <Autocomplete
                options={devotees}
                getOptionLabel={(option) => `${option.name} - ${option.phone || ''}`}
                onInputChange={(e, value) => {
                  if (value) loadDevotees(value);
                }}
                onChange={(e, value) => {
                  if (value) {
                    setSaleForm({
                      ...saleForm,
                      devotee_id: value.id,
                      devotee_name: value.name,
                      devotee_phone: value.phone || '',
                    });
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Devotee (Optional)"
                    placeholder="Search devotee..."
                  />
                )}
              />
              <TextField
                label="Devotee Name"
                value={saleForm.devotee_name}
                onChange={(e) => setSaleForm({ ...saleForm, devotee_name: e.target.value })}
                fullWidth
              />
              <TextField
                label="Devotee Phone"
                value={saleForm.devotee_phone}
                onChange={(e) => setSaleForm({ ...saleForm, devotee_phone: e.target.value })}
                fullWidth
              />
              <TextField
                label="Notes"
                value={saleForm.notes}
                onChange={(e) => setSaleForm({ ...saleForm, notes: e.target.value })}
                fullWidth
                multiline
                rows={2}
              />
              <Button
                variant="contained"
                onClick={handleSale}
                disabled={loading}
                fullWidth
                size="large"
              >
                Record Sale
              </Button>
            </Stack>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Recent Sales</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Token</TableCell>
                    <TableCell>Seva</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Payment</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sales.slice(0, 10).map((sale) => (
                    <TableRow key={sale.id}>
                      <TableCell>{sale.token_serial_number}</TableCell>
                      <TableCell>{sale.seva_name}</TableCell>
                      <TableCell>₹{sale.amount}</TableCell>
                      <TableCell>
                        <Chip
                          label={sale.payment_mode}
                          size="small"
                          color={sale.payment_mode === 'cash' ? 'primary' : 'success'}
                        />
                      </TableCell>
                      <TableCell>{new Date(sale.sale_date).toLocaleDateString()}</TableCell>
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

  const renderQueueTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Token Queue</Typography>
        <IconButton onClick={loadQueue}>
          <RefreshIcon />
        </IconButton>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Token Serial</TableCell>
              <TableCell>Seva</TableCell>
              <TableCell>Devotee</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Payment</TableCell>
              <TableCell>Counter</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {queue.map((item) => (
              <TableRow key={item.id}>
                <TableCell>
                  {new Date(item.sale_date).toLocaleTimeString()}
                </TableCell>
                <TableCell>
                  <Chip label={item.token_serial_number} size="small" />
                </TableCell>
                <TableCell>{item.seva_name}</TableCell>
                <TableCell>{item.devotee_name || 'Anonymous'}</TableCell>
                <TableCell>₹{item.amount}</TableCell>
                <TableCell>
                  <Chip
                    label={item.payment_mode}
                    size="small"
                    color={item.payment_mode === 'cash' ? 'primary' : 'success'}
                  />
                </TableCell>
                <TableCell>{item.counter_number || '-'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderReconciliationTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Daily Reconciliation</Typography>
        <Button
          variant="contained"
          onClick={handleCreateReconciliation}
          disabled={loading || reconciliationData}
        >
          Create Reconciliation
        </Button>
      </Box>

      {reconciliationData ? (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6">
              Reconciliation for {new Date(reconciliationData.date).toLocaleDateString()}
            </Typography>
            {!reconciliationData.is_reconciled && (
              <Button
                variant="contained"
                color="success"
                startIcon={<CheckCircleIcon />}
                onClick={() => handleApproveReconciliation(reconciliationData.id)}
                disabled={loading}
              >
                Approve Reconciliation
              </Button>
            )}
            {reconciliationData.is_reconciled && (
              <Chip
                label="Reconciled"
                color="success"
                icon={<CheckCircleIcon />}
              />
            )}
          </Box>

          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">Total Tokens Sold</Typography>
                  <Typography variant="h4">{reconciliationData.total_tokens_sold}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">Total Amount</Typography>
                  <Typography variant="h4">₹{reconciliationData.total_amount}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">Cash</Typography>
                  <Typography variant="h4">₹{reconciliationData.total_amount_cash}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography variant="body2" color="text.secondary">UPI</Typography>
                  <Typography variant="h4">₹{reconciliationData.total_amount_upi}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {reconciliationData.counter_summary && (
            <Box mb={3}>
              <Typography variant="h6" mb={2}>Counter Summary</Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Counter</TableCell>
                      <TableCell>Tokens Sold</TableCell>
                      <TableCell>Cash</TableCell>
                      <TableCell>UPI</TableCell>
                      <TableCell>Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(reconciliationData.counter_summary).map(([counter, data]) => (
                      <TableRow key={counter}>
                        <TableCell>{counter}</TableCell>
                        <TableCell>{data.tokens_sold}</TableCell>
                        <TableCell>₹{data.cash}</TableCell>
                        <TableCell>₹{data.upi}</TableCell>
                        <TableCell>₹{data.total}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {reconciliationData.discrepancy_notes && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="subtitle2">Discrepancy Notes:</Typography>
              <Typography>{reconciliationData.discrepancy_notes}</Typography>
            </Alert>
          )}
        </Paper>
      ) : (
        <Alert severity="info">
          No reconciliation found for today. Click "Create Reconciliation" to generate one.
        </Alert>
      )}
    </Box>
  );

  return (
    <Layout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Token Seva Management
        </Typography>

        <Paper sx={{ mt: 2 }}>
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<InventoryIcon />} iconPosition="start" label="Inventory" />
            <Tab icon={<PointOfSaleIcon />} iconPosition="start" label="Sales" />
            <Tab icon={<QueueIcon />} iconPosition="start" label="Queue" />
            <Tab icon={<AssessmentIcon />} iconPosition="start" label="Reconciliation" />
          </Tabs>

          <Box sx={{ p: 3 }}>
            {loading && (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            )}

            {!loading && tabValue === 0 && renderInventoryTab()}
            {!loading && tabValue === 1 && renderSaleTab()}
            {!loading && tabValue === 2 && renderQueueTab()}
            {!loading && tabValue === 3 && renderReconciliationTab()}
          </Box>
        </Paper>
      </Box>
    </Layout>
  );
}

export default TokenSeva;



