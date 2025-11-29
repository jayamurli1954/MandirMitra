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
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import SecurityIcon from '@mui/icons-material/Security';
import DescriptionIcon from '@mui/icons-material/Description';
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

const AssetManagementAdvanced = () => {
  const { showSuccess, showError } = useNotification();
  const [activeTab, setActiveTab] = useState(0);
  const [assets, setAssets] = useState([]);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Transfer state
  const [transfers, setTransfers] = useState([]);
  const [transferDialogOpen, setTransferDialogOpen] = useState(false);
  const [transferForm, setTransferForm] = useState({
    transfer_date: new Date(),
    to_location: '',
    transfer_reason: '',
    notes: '',
  });
  
  // Physical Verification state
  const [verifications, setVerifications] = useState([]);
  const [verificationDialogOpen, setVerificationDialogOpen] = useState(false);
  const [verificationForm, setVerificationForm] = useState({
    verification_date: new Date(),
    verified_location: '',
    condition: 'GOOD',
    condition_notes: '',
    verified_by_second: null,
    notes: '',
  });
  
  // Insurance state
  const [insurances, setInsurances] = useState([]);
  const [insuranceDialogOpen, setInsuranceDialogOpen] = useState(false);
  const [insuranceForm, setInsuranceForm] = useState({
    policy_number: '',
    insurance_company: '',
    policy_start_date: new Date(),
    policy_end_date: new Date(),
    premium_amount: 0,
    insured_value: 0,
    coverage_type: '',
    coverage_details: '',
    auto_renewal: false,
    renewal_reminder_days: 30,
    agent_name: '',
    agent_contact: '',
    notes: '',
  });
  
  // Documents state
  const [documents, setDocuments] = useState([]);
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false);
  const [documentFile, setDocumentFile] = useState(null);
  const [documentForm, setDocumentForm] = useState({
    document_type: '',
    document_name: '',
    description: '',
  });
  
  // Users for second verification
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetchAssets();
    fetchUsers();
  }, []);

  useEffect(() => {
    if (selectedAsset) {
      if (activeTab === 0) fetchTransfers();
      if (activeTab === 1) fetchVerifications();
      if (activeTab === 2) fetchInsurances();
      if (activeTab === 3) fetchDocuments();
    }
  }, [selectedAsset, activeTab]);

  const fetchAssets = async () => {
    try {
      const response = await api.get('/api/v1/assets/');
      setAssets(response.data.filter(a => a.status === 'active'));
    } catch (err) {
      showError('Failed to load assets');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/v1/users/');
      setUsers(response.data || []);
    } catch (err) {
      console.error('Failed to load users');
    }
  };

  const fetchTransfers = async () => {
    if (!selectedAsset) return;
    try {
      const response = await api.get(`/api/v1/assets/${selectedAsset.id}/transfers`);
      setTransfers(response.data || []);
    } catch (err) {
      showError('Failed to load transfers');
    }
  };

  const fetchVerifications = async () => {
    if (!selectedAsset) return;
    try {
      const response = await api.get(`/api/v1/assets/${selectedAsset.id}/physical-verifications`);
      setVerifications(response.data || []);
    } catch (err) {
      showError('Failed to load verifications');
    }
  };

  const fetchInsurances = async () => {
    if (!selectedAsset) return;
    try {
      const response = await api.get(`/api/v1/assets/${selectedAsset.id}/insurance`);
      setInsurances(response.data || []);
    } catch (err) {
      showError('Failed to load insurance policies');
    }
  };

  const fetchDocuments = async () => {
    if (!selectedAsset) return;
    try {
      const response = await api.get(`/api/v1/assets/${selectedAsset.id}/documents`);
      setDocuments(response.data || []);
    } catch (err) {
      showError('Failed to load documents');
    }
  };

  const handleTransfer = async () => {
    if (!selectedAsset) {
      showError('Please select an asset');
      return;
    }
    if (!transferForm.to_location) {
      showError('Please enter destination location');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/api/v1/assets/${selectedAsset.id}/transfer`, {
        ...transferForm,
        transfer_date: transferForm.transfer_date.toISOString().split('T')[0],
      });
      showSuccess('Asset transfer recorded');
      setTransferDialogOpen(false);
      setTransferForm({
        transfer_date: new Date(),
        to_location: '',
        transfer_reason: '',
        notes: '',
      });
      fetchTransfers();
      fetchAssets();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to transfer asset');
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async () => {
    if (!selectedAsset) {
      showError('Please select an asset');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/api/v1/assets/${selectedAsset.id}/physical-verification`, {
        ...verificationForm,
        verification_date: verificationForm.verification_date.toISOString().split('T')[0],
      });
      showSuccess('Physical verification recorded');
      setVerificationDialogOpen(false);
      setVerificationForm({
        verification_date: new Date(),
        verified_location: '',
        condition: 'GOOD',
        condition_notes: '',
        verified_by_second: null,
        notes: '',
      });
      fetchVerifications();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to record verification');
    } finally {
      setLoading(false);
    }
  };

  const handleAddInsurance = async () => {
    if (!selectedAsset) {
      showError('Please select an asset');
      return;
    }
    if (!insuranceForm.policy_number || !insuranceForm.insurance_company) {
      showError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/api/v1/assets/${selectedAsset.id}/insurance`, {
        ...insuranceForm,
        policy_start_date: insuranceForm.policy_start_date.toISOString().split('T')[0],
        policy_end_date: insuranceForm.policy_end_date.toISOString().split('T')[0],
      });
      showSuccess('Insurance policy added');
      setInsuranceDialogOpen(false);
      setInsuranceForm({
        policy_number: '',
        insurance_company: '',
        policy_start_date: new Date(),
        policy_end_date: new Date(),
        premium_amount: 0,
        insured_value: 0,
        coverage_type: '',
        coverage_details: '',
        auto_renewal: false,
        renewal_reminder_days: 30,
        agent_name: '',
        agent_contact: '',
        notes: '',
      });
      fetchInsurances();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to add insurance');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDocument = async () => {
    if (!selectedAsset) {
      showError('Please select an asset');
      return;
    }
    if (!documentFile || !documentForm.document_type) {
      showError('Please select a file and document type');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', documentFile);
      formData.append('document_type', documentForm.document_type);
      formData.append('document_name', documentForm.document_name);
      formData.append('description', documentForm.description || '');

      await api.post(`/api/v1/assets/${selectedAsset.id}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      showSuccess('Document uploaded successfully');
      setDocumentDialogOpen(false);
      setDocumentFile(null);
      setDocumentForm({
        document_type: '',
        document_name: '',
        description: '',
      });
      fetchDocuments();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setLoading(false);
    }
  };

  const renderTransferTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Asset Transfer History</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setTransferDialogOpen(true)}
          disabled={!selectedAsset}
        >
          Transfer Asset
        </Button>
      </Box>

      {selectedAsset && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Selected Asset: <strong>{selectedAsset.asset_number} - {selectedAsset.asset_name}</strong>
          {selectedAsset.location && ` (Current Location: ${selectedAsset.location})`}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>From Location</TableCell>
              <TableCell>To Location</TableCell>
              <TableCell>Reason</TableCell>
              <TableCell>Transferred By</TableCell>
              <TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transfers.map((transfer) => (
              <TableRow key={transfer.id}>
                <TableCell>{new Date(transfer.transfer_date).toLocaleDateString()}</TableCell>
                <TableCell>{transfer.from_location || '-'}</TableCell>
                <TableCell>{transfer.to_location}</TableCell>
                <TableCell>{transfer.transfer_reason || '-'}</TableCell>
                <TableCell>{transfer.transferred_by_name || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={transfer.approved_at ? 'Approved' : 'Pending'}
                    color={transfer.approved_at ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={transferDialogOpen} onClose={() => setTransferDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Transfer Asset</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Transfer Date"
                value={transferForm.transfer_date}
                onChange={(date) => setTransferForm({ ...transferForm, transfer_date: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
            <TextField
              label="To Location"
              value={transferForm.to_location}
              onChange={(e) => setTransferForm({ ...transferForm, to_location: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Transfer Reason"
              value={transferForm.transfer_reason}
              onChange={(e) => setTransferForm({ ...transferForm, transfer_reason: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <TextField
              label="Notes"
              value={transferForm.notes}
              onChange={(e) => setTransferForm({ ...transferForm, notes: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTransferDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleTransfer} variant="contained" disabled={loading}>
            Transfer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderVerificationTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Physical Verification History</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setVerificationDialogOpen(true)}
          disabled={!selectedAsset}
        >
          Record Verification
        </Button>
      </Box>

      {selectedAsset && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Selected Asset: <strong>{selectedAsset.asset_number} - {selectedAsset.asset_name}</strong>
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Condition</TableCell>
              <TableCell>Verified By</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Discrepancy</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {verifications.map((verification) => (
              <TableRow key={verification.id}>
                <TableCell>{new Date(verification.verification_date).toLocaleDateString()}</TableCell>
                <TableCell>{verification.verified_location}</TableCell>
                <TableCell>
                  <Chip
                    label={verification.condition}
                    color={
                      verification.condition === 'GOOD' ? 'success' :
                      verification.condition === 'FAIR' ? 'warning' : 'error'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>{verification.verified_by_name || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={verification.status}
                    color={verification.status === 'APPROVED' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {verification.has_discrepancy ? (
                    <Chip label="Yes" color="error" size="small" icon={<WarningIcon />} />
                  ) : (
                    <Chip label="No" color="success" size="small" />
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={verificationDialogOpen} onClose={() => setVerificationDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Record Physical Verification</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Verification Date"
                value={verificationForm.verification_date}
                onChange={(date) => setVerificationForm({ ...verificationForm, verification_date: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
            <TextField
              label="Verified Location"
              value={verificationForm.verified_location}
              onChange={(e) => setVerificationForm({ ...verificationForm, verified_location: e.target.value })}
              fullWidth
              required
            />
            <TextField
              select
              label="Condition"
              value={verificationForm.condition}
              onChange={(e) => setVerificationForm({ ...verificationForm, condition: e.target.value })}
              fullWidth
              required
            >
              <MenuItem value="GOOD">Good</MenuItem>
              <MenuItem value="FAIR">Fair</MenuItem>
              <MenuItem value="POOR">Poor</MenuItem>
              <MenuItem value="DAMAGED">Damaged</MenuItem>
            </TextField>
            <TextField
              label="Condition Notes"
              value={verificationForm.condition_notes}
              onChange={(e) => setVerificationForm({ ...verificationForm, condition_notes: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <TextField
              select
              label="Second Verifier (Optional)"
              value={verificationForm.verified_by_second || ''}
              onChange={(e) => setVerificationForm({ ...verificationForm, verified_by_second: e.target.value || null })}
              fullWidth
            >
              <MenuItem value="">None</MenuItem>
              {users.map((user) => (
                <MenuItem key={user.id} value={user.id}>
                  {user.name || user.email}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Notes"
              value={verificationForm.notes}
              onChange={(e) => setVerificationForm({ ...verificationForm, notes: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerificationDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleVerification} variant="contained" disabled={loading}>
            Record Verification
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderInsuranceTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Insurance Policies</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setInsuranceDialogOpen(true)}
          disabled={!selectedAsset}
        >
          Add Insurance
        </Button>
      </Box>

      {selectedAsset && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Selected Asset: <strong>{selectedAsset.asset_number} - {selectedAsset.asset_name}</strong>
        </Alert>
      )}

      <Grid container spacing={2}>
        {insurances.map((insurance) => (
          <Grid item xs={12} md={6} key={insurance.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                  <Box>
                    <Typography variant="h6">{insurance.insurance_company}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Policy: {insurance.policy_number}
                    </Typography>
                  </Box>
                  <Chip
                    label={insurance.is_active ? 'Active' : 'Expired'}
                    color={insurance.is_active ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
                <Stack spacing={1}>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Coverage:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      ₹{insurance.insured_value.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Premium:</Typography>
                    <Typography variant="body2">₹{insurance.premium_amount.toLocaleString()}</Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="body2">Valid Until:</Typography>
                    <Typography variant="body2">
                      {new Date(insurance.policy_end_date).toLocaleDateString()}
                    </Typography>
                  </Box>
                  {insurance.days_until_expiry !== undefined && insurance.days_until_expiry < 30 && (
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      Expires in {insurance.days_until_expiry} days
                    </Alert>
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={insuranceDialogOpen} onClose={() => setInsuranceDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Insurance Policy</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Policy Number"
              value={insuranceForm.policy_number}
              onChange={(e) => setInsuranceForm({ ...insuranceForm, policy_number: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Insurance Company"
              value={insuranceForm.insurance_company}
              onChange={(e) => setInsuranceForm({ ...insuranceForm, insurance_company: e.target.value })}
              fullWidth
              required
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Policy Start Date"
                    value={insuranceForm.policy_start_date}
                    onChange={(date) => setInsuranceForm({ ...insuranceForm, policy_start_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={6}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Policy End Date"
                    value={insuranceForm.policy_end_date}
                    onChange={(date) => setInsuranceForm({ ...insuranceForm, policy_end_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Premium Amount"
                  type="number"
                  value={insuranceForm.premium_amount}
                  onChange={(e) => setInsuranceForm({ ...insuranceForm, premium_amount: parseFloat(e.target.value) || 0 })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Insured Value"
                  type="number"
                  value={insuranceForm.insured_value}
                  onChange={(e) => setInsuranceForm({ ...insuranceForm, insured_value: parseFloat(e.target.value) || 0 })}
                  fullWidth
                  required
                />
              </Grid>
            </Grid>
            <TextField
              label="Coverage Type"
              value={insuranceForm.coverage_type}
              onChange={(e) => setInsuranceForm({ ...insuranceForm, coverage_type: e.target.value })}
              fullWidth
            />
            <TextField
              label="Coverage Details"
              value={insuranceForm.coverage_details}
              onChange={(e) => setInsuranceForm({ ...insuranceForm, coverage_details: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Agent Name"
                  value={insuranceForm.agent_name}
                  onChange={(e) => setInsuranceForm({ ...insuranceForm, agent_name: e.target.value })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Agent Contact"
                  value={insuranceForm.agent_contact}
                  onChange={(e) => setInsuranceForm({ ...insuranceForm, agent_contact: e.target.value })}
                  fullWidth
                />
              </Grid>
            </Grid>
            <TextField
              label="Notes"
              value={insuranceForm.notes}
              onChange={(e) => setInsuranceForm({ ...insuranceForm, notes: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInsuranceDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddInsurance} variant="contained" disabled={loading}>
            Add Insurance
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderDocumentsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Asset Documents</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDocumentDialogOpen(true)}
          disabled={!selectedAsset}
        >
          Upload Document
        </Button>
      </Box>

      {selectedAsset && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Selected Asset: <strong>{selectedAsset.asset_number} - {selectedAsset.asset_name}</strong>
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Document Type</TableCell>
              <TableCell>Document Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Uploaded Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell>{doc.document_type}</TableCell>
                <TableCell>{doc.document_name}</TableCell>
                <TableCell>{doc.description || '-'}</TableCell>
                <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => window.open(doc.document_url, '_blank')}
                  >
                    <AttachFileIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={documentDialogOpen} onClose={() => setDocumentDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              select
              label="Document Type"
              value={documentForm.document_type}
              onChange={(e) => setDocumentForm({ ...documentForm, document_type: e.target.value })}
              fullWidth
              required
            >
              <MenuItem value="purchase_invoice">Purchase Invoice</MenuItem>
              <MenuItem value="warranty">Warranty</MenuItem>
              <MenuItem value="insurance">Insurance</MenuItem>
              <MenuItem value="appraisal">Appraisal</MenuItem>
              <MenuItem value="maintenance">Maintenance Record</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </TextField>
            <TextField
              label="Document Name"
              value={documentForm.document_name}
              onChange={(e) => setDocumentForm({ ...documentForm, document_name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Description"
              value={documentForm.description}
              onChange={(e) => setDocumentForm({ ...documentForm, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadFileIcon />}
              fullWidth
            >
              Select File
              <input
                type="file"
                hidden
                onChange={(e) => setDocumentFile(e.target.files[0])}
              />
            </Button>
            {documentFile && (
              <Alert severity="info">
                Selected: {documentFile.name}
              </Alert>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDocumentDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUploadDocument} variant="contained" disabled={loading || !documentFile}>
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Asset Management - Advanced Features
        </Typography>

        <Paper sx={{ mt: 2 }}>
          <Box sx={{ p: 2 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Select Asset</InputLabel>
              <Select
                value={selectedAsset?.id || ''}
                onChange={(e) => {
                  const asset = assets.find(a => a.id === e.target.value);
                  setSelectedAsset(asset);
                }}
                label="Select Asset"
              >
                {assets.map((asset) => (
                  <MenuItem key={asset.id} value={asset.id}>
                    {asset.asset_number} - {asset.asset_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>

          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<LocationOnIcon />} iconPosition="start" label="Transfers" />
            <Tab icon={<VerifiedUserIcon />} iconPosition="start" label="Physical Verification" />
            <Tab icon={<SecurityIcon />} iconPosition="start" label="Insurance" />
            <Tab icon={<DescriptionIcon />} iconPosition="start" label="Documents" />
          </Tabs>

          <Box sx={{ p: 3 }}>
            {loading && (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            )}

            {!loading && activeTab === 0 && renderTransferTab()}
            {!loading && activeTab === 1 && renderVerificationTab()}
            {!loading && activeTab === 2 && renderInsuranceTab()}
            {!loading && activeTab === 3 && renderDocumentsTab()}
          </Box>
        </Paper>
      </Container>
    </Layout>
  );
};

export default AssetManagementAdvanced;

