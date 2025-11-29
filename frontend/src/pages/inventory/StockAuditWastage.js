import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  IconButton,
  Stack,
  InputLabel,
  FormControl,
  Select,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import InventoryIcon from '@mui/icons-material/Inventory';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import Layout from '../../components/Layout';
import api from '../../services/api';
import { useNotification } from '../../contexts/NotificationContext';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

function TabPanel({ children, value, index }) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const StockAuditWastage = () => {
  const { showSuccess, showError } = useNotification();
  const [activeTab, setActiveTab] = useState(0);
  const [stores, setStores] = useState([]);
  const [items, setItems] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Stock Audit state
  const [audits, setAudits] = useState([]);
  const [auditDialogOpen, setAuditDialogOpen] = useState(false);
  const [auditItems, setAuditItems] = useState([]);
  const [auditForm, setAuditForm] = useState({
    audit_date: new Date(),
    store_id: '',
    notes: '',
  });
  const [currentAuditItem, setCurrentAuditItem] = useState({
    item_id: '',
    physical_quantity: '',
    discrepancy_reason: '',
    notes: '',
  });
  
  // Wastage state
  const [wastages, setWastages] = useState([]);
  const [wastageDialogOpen, setWastageDialogOpen] = useState(false);
  const [wastageForm, setWastageForm] = useState({
    wastage_date: new Date(),
    item_id: '',
    store_id: '',
    quantity: '',
    reason: 'expired',
    notes: '',
  });

  useEffect(() => {
    fetchStores();
    fetchItems();
    if (activeTab === 0) fetchAudits();
    if (activeTab === 1) fetchWastages();
  }, [activeTab]);

  const fetchStores = async () => {
    try {
      const response = await api.get('/api/v1/inventory/stores/');
      setStores(response.data || []);
    } catch (err) {
      showError('Failed to load stores');
    }
  };

  const fetchItems = async () => {
    try {
      const response = await api.get('/api/v1/inventory/items/', { params: { is_active: true } });
      setItems(response.data || []);
    } catch (err) {
      showError('Failed to load items');
    }
  };

  const fetchAudits = async () => {
    try {
      const response = await api.get('/api/v1/inventory/audits');
      setAudits(response.data || []);
    } catch (err) {
      showError('Failed to load audits');
    }
  };

  const fetchWastages = async () => {
    try {
      const response = await api.get('/api/v1/inventory/wastages');
      setWastages(response.data || []);
    } catch (err) {
      showError('Failed to load wastages');
    }
  };

  const handleStartAudit = () => {
    if (!auditForm.store_id) {
      showError('Please select a store');
      return;
    }
    setAuditItems([]);
    setAuditDialogOpen(true);
  };

  const handleAddAuditItem = () => {
    if (!currentAuditItem.item_id || !currentAuditItem.physical_quantity) {
      showError('Please fill all required fields');
      return;
    }
    const item = items.find(i => i.id === parseInt(currentAuditItem.item_id));
    setAuditItems([
      ...auditItems,
      {
        ...currentAuditItem,
        item_name: item?.name || '',
        item_code: item?.code || '',
      },
    ]);
    setCurrentAuditItem({
      item_id: '',
      physical_quantity: '',
      discrepancy_reason: '',
      notes: '',
    });
  };

  const handleRemoveAuditItem = (index) => {
    setAuditItems(auditItems.filter((_, i) => i !== index));
  };

  const handleSubmitAudit = async () => {
    if (auditItems.length === 0) {
      showError('Please add at least one audit item');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/v1/inventory/audits', {
        audit_date: auditForm.audit_date.toISOString().split('T')[0],
        store_id: parseInt(auditForm.store_id),
        notes: auditForm.notes,
        items: auditItems.map(item => ({
          item_id: parseInt(item.item_id),
          physical_quantity: parseFloat(item.physical_quantity),
          discrepancy_reason: item.discrepancy_reason,
          notes: item.notes,
        })),
      });
      showSuccess('Stock audit created successfully');
      setAuditDialogOpen(false);
      setAuditForm({
        audit_date: new Date(),
        store_id: '',
        notes: '',
      });
      setAuditItems([]);
      fetchAudits();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create audit');
    } finally {
      setLoading(false);
    }
  };

  const handleRecordWastage = async () => {
    if (!wastageForm.item_id || !wastageForm.store_id || !wastageForm.quantity) {
      showError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v1/inventory/wastages', {
        wastage_date: wastageForm.wastage_date.toISOString().split('T')[0],
        item_id: parseInt(wastageForm.item_id),
        store_id: parseInt(wastageForm.store_id),
        quantity: parseFloat(wastageForm.quantity),
        unit_cost: 0, // Will be calculated from stock balance
        reason: wastageForm.reason,
        reason_details: wastageForm.notes,
        notes: wastageForm.notes,
      });
      showSuccess('Wastage recorded successfully');
      setWastageDialogOpen(false);
      setWastageForm({
        wastage_date: new Date(),
        item_id: '',
        store_id: '',
        quantity: '',
        reason: 'expired',
        notes: '',
      });
      fetchWastages();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to record wastage');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAudit = async (auditId) => {
    setLoading(true);
    try {
      await api.put(`/api/v1/inventory/audits/${auditId}/approve`);
      showSuccess('Audit approved');
      fetchAudits();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to approve audit');
    } finally {
      setLoading(false);
    }
  };

  const renderAuditTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Stock Audits</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleStartAudit}
        >
          New Audit
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Audit Date</TableCell>
              <TableCell>Store</TableCell>
              <TableCell>Items Audited</TableCell>
              <TableCell>Discrepancies</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {audits.map((audit) => (
              <TableRow key={audit.id}>
                <TableCell>{new Date(audit.audit_date).toLocaleDateString()}</TableCell>
                <TableCell>{audit.store_name || '-'}</TableCell>
                <TableCell>{audit.total_items || 0}</TableCell>
                <TableCell>
                  {audit.total_discrepancies > 0 ? (
                    <Chip label={audit.total_discrepancies} color="error" size="small" />
                  ) : (
                    <Chip label="None" color="success" size="small" />
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={audit.status}
                    color={audit.status === 'APPROVED' ? 'success' : audit.status === 'PENDING' ? 'warning' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {audit.status === 'PENDING' && (
                    <IconButton
                      size="small"
                      color="success"
                      onClick={() => handleApproveAudit(audit.id)}
                    >
                      <CheckCircleIcon />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={auditDialogOpen} onClose={() => setAuditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Stock Audit</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Audit Date"
                value={auditForm.audit_date}
                onChange={(date) => setAuditForm({ ...auditForm, audit_date: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
            <TextField
              select
              label="Store"
              value={auditForm.store_id}
              onChange={(e) => setAuditForm({ ...auditForm, store_id: e.target.value })}
              fullWidth
              required
            >
              {stores.map((store) => (
                <MenuItem key={store.id} value={store.id}>
                  {store.name}
                </MenuItem>
              ))}
            </TextField>
            
            <Typography variant="subtitle2" sx={{ mt: 2 }}>Audit Items</Typography>
            <Stack spacing={2}>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    select
                    label="Item"
                    value={currentAuditItem.item_id}
                    onChange={(e) => setCurrentAuditItem({ ...currentAuditItem, item_id: e.target.value })}
                    fullWidth
                    size="small"
                  >
                    {items.map((item) => (
                      <MenuItem key={item.id} value={item.id}>
                        {item.code} - {item.name}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={3}>
                  <TextField
                    label="Physical Qty"
                    type="number"
                    value={currentAuditItem.physical_quantity}
                    onChange={(e) => setCurrentAuditItem({ ...currentAuditItem, physical_quantity: e.target.value })}
                    fullWidth
                    size="small"
                  />
                </Grid>
                <Grid item xs={3}>
                  <TextField
                    label="Reason"
                    value={currentAuditItem.discrepancy_reason}
                    onChange={(e) => setCurrentAuditItem({ ...currentAuditItem, discrepancy_reason: e.target.value })}
                    fullWidth
                    size="small"
                  />
                </Grid>
                <Grid item xs={2}>
                  <Button
                    variant="contained"
                    onClick={handleAddAuditItem}
                    fullWidth
                    size="small"
                  >
                    Add
                  </Button>
                </Grid>
              </Grid>

              {auditItems.length > 0 && (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell>Physical Qty</TableCell>
                        <TableCell>Reason</TableCell>
                        <TableCell>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {auditItems.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>{item.item_name}</TableCell>
                          <TableCell>{item.physical_quantity}</TableCell>
                          <TableCell>{item.discrepancy_reason || '-'}</TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              onClick={() => handleRemoveAuditItem(index)}
                            >
                              <DeleteForeverIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Stack>

            <TextField
              label="Notes"
              value={auditForm.notes}
              onChange={(e) => setAuditForm({ ...auditForm, notes: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmitAudit} variant="contained" disabled={loading}>
            Create Audit
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderWastageTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Stock Wastage</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setWastageDialogOpen(true)}
        >
          Record Wastage
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Item</TableCell>
              <TableCell>Store</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Reason</TableCell>
              <TableCell>Notes</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {wastages.map((wastage) => (
              <TableRow key={wastage.id}>
                <TableCell>{new Date(wastage.wastage_date).toLocaleDateString()}</TableCell>
                <TableCell>{wastage.item_name || '-'}</TableCell>
                <TableCell>{wastage.store_name || '-'}</TableCell>
                <TableCell>{wastage.quantity} {wastage.unit || ''}</TableCell>
                <TableCell>
                  <Chip label={wastage.reason} size="small" color="error" />
                </TableCell>
                <TableCell>{wastage.notes || '-'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={wastageDialogOpen} onClose={() => setWastageDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Record Stock Wastage</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Wastage Date"
                value={wastageForm.wastage_date}
                onChange={(date) => setWastageForm({ ...wastageForm, wastage_date: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
            <TextField
              select
              label="Store"
              value={wastageForm.store_id}
              onChange={(e) => setWastageForm({ ...wastageForm, store_id: e.target.value })}
              fullWidth
              required
            >
              {stores.map((store) => (
                <MenuItem key={store.id} value={store.id}>
                  {store.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Item"
              value={wastageForm.item_id}
              onChange={(e) => setWastageForm({ ...wastageForm, item_id: e.target.value })}
              fullWidth
              required
            >
              {items.map((item) => (
                <MenuItem key={item.id} value={item.id}>
                  {item.code} - {item.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Quantity"
              type="number"
              value={wastageForm.quantity}
              onChange={(e) => setWastageForm({ ...wastageForm, quantity: e.target.value })}
              fullWidth
              required
            />
            <TextField
              select
              label="Reason"
              value={wastageForm.reason}
              onChange={(e) => setWastageForm({ ...wastageForm, reason: e.target.value })}
              fullWidth
              required
            >
              <MenuItem value="expired">Expired</MenuItem>
              <MenuItem value="damaged">Damaged</MenuItem>
              <MenuItem value="spoiled">Spoiled</MenuItem>
              <MenuItem value="theft">Theft</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </TextField>
            <TextField
              label="Notes"
              value={wastageForm.notes}
              onChange={(e) => setWastageForm({ ...wastageForm, notes: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWastageDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleRecordWastage} variant="contained" disabled={loading}>
            Record Wastage
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Stock Audit & Wastage Management
        </Typography>

        <Paper sx={{ mt: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<InventoryIcon />} iconPosition="start" label="Stock Audit" />
            <Tab icon={<DeleteForeverIcon />} iconPosition="start" label="Wastage Recording" />
          </Tabs>

          <Box sx={{ p: 3 }}>
            {loading && (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            )}

            {!loading && activeTab === 0 && renderAuditTab()}
            {!loading && activeTab === 1 && renderWastageTab()}
          </Box>
        </Paper>
      </Container>
    </Layout>
  );
};

export default StockAuditWastage;

