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
  Autocomplete,
  InputLabel,
  FormControl,
  Select,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import DescriptionIcon from '@mui/icons-material/Description';
import GavelIcon from '@mui/icons-material/Gavel';
import AssessmentIcon from '@mui/icons-material/Assessment';
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

const TenderManagement = () => {
  const { showSuccess, showError } = useNotification();
  const [activeTab, setActiveTab] = useState(0);
  const [tenders, setTenders] = useState([]);
  const [selectedTender, setSelectedTender] = useState(null);
  const [bids, setBids] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Tender form state
  const [tenderDialogOpen, setTenderDialogOpen] = useState(false);
  const [tenderForm, setTenderForm] = useState({
    title: '',
    description: '',
    tender_type: 'asset_procurement',
    estimated_value: 0,
    tender_issue_date: new Date(),
    last_date_submission: new Date(),
    opening_date: new Date(),
    terms_conditions: '',
  });
  
  // Bid form state
  const [bidDialogOpen, setBidDialogOpen] = useState(false);
  const [bidForm, setBidForm] = useState({
    vendor_id: '',
    bid_amount: 0,
    bid_date: new Date(),
    validity_period_days: 90,
    technical_specifications: '',
  });
  
  // Document upload state
  const [documentDialogOpen, setDocumentDialogOpen] = useState(false);
  const [documentFile, setDocumentFile] = useState(null);
  const [documentType, setDocumentType] = useState('tender');
  const [isBidDocument, setIsBidDocument] = useState(false);
  const [selectedBid, setSelectedBid] = useState(null);
  
  // Bid comparison state
  const [comparisonData, setComparisonData] = useState(null);
  const [comparisonDialogOpen, setComparisonDialogOpen] = useState(false);

  useEffect(() => {
    fetchTenders();
    fetchVendors();
  }, []);

  useEffect(() => {
    if (selectedTender && activeTab === 1) {
      fetchBids();
    }
  }, [selectedTender, activeTab]);

  const fetchTenders = async () => {
    try {
      const response = await api.get('/api/v1/tenders/');
      setTenders(response.data || []);
    } catch (err) {
      showError('Failed to load tenders');
    }
  };

  const fetchVendors = async () => {
    try {
      const response = await api.get('/api/v1/vendors/');
      setVendors(response.data || []);
    } catch (err) {
      console.error('Failed to load vendors');
    }
  };

  const fetchBids = async () => {
    if (!selectedTender) return;
    try {
      const response = await api.get(`/api/v1/tenders/${selectedTender.id}/bids`);
      setBids(response.data || []);
    } catch (err) {
      showError('Failed to load bids');
    }
  };

  const handleCreateTender = async () => {
    if (!tenderForm.title || !tenderForm.tender_type) {
      showError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v1/tenders/', {
        ...tenderForm,
        tender_issue_date: tenderForm.tender_issue_date.toISOString().split('T')[0],
        last_date_submission: tenderForm.last_date_submission.toISOString().split('T')[0],
        opening_date: tenderForm.opening_date.toISOString().split('T')[0],
      });
      showSuccess('Tender created successfully');
      setTenderDialogOpen(false);
      setTenderForm({
        title: '',
        description: '',
        tender_type: 'asset_procurement',
        estimated_value: 0,
        tender_issue_date: new Date(),
        last_date_submission: new Date(),
        opening_date: new Date(),
        terms_conditions: '',
      });
      fetchTenders();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to create tender');
    } finally {
      setLoading(false);
    }
  };

  const handlePublishTender = async (tenderId) => {
    setLoading(true);
    try {
      await api.post(`/api/v1/tenders/${tenderId}/publish`);
      showSuccess('Tender published');
      fetchTenders();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to publish tender');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitBid = async () => {
    if (!selectedTender || !bidForm.vendor_id || !bidForm.bid_amount) {
      showError('Please fill all required fields');
      return;
    }

    setLoading(true);
    try {
      await api.post(`/api/v1/tenders/${selectedTender.id}/bids`, {
        ...bidForm,
        bid_date: bidForm.bid_date.toISOString().split('T')[0],
      });
      showSuccess('Bid submitted successfully');
      setBidDialogOpen(false);
      setBidForm({
        vendor_id: '',
        bid_amount: 0,
        bid_date: new Date(),
        validity_period_days: 90,
        technical_specifications: '',
      });
      fetchBids();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to submit bid');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDocument = async () => {
    if (!documentFile) {
      showError('Please select a file');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', documentFile);
      if (documentType) {
        formData.append('document_type', documentType);
      }

      if (isBidDocument && selectedBid) {
        await api.post(`/api/v1/tenders/bids/${selectedBid.id}/documents`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        showSuccess('Bid document uploaded');
      } else if (selectedTender) {
        await api.post(`/api/v1/tenders/${selectedTender.id}/documents`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        showSuccess('Tender document uploaded');
      }
      
      setDocumentDialogOpen(false);
      setDocumentFile(null);
      setDocumentType('tender');
      setIsBidDocument(false);
      setSelectedBid(null);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setLoading(false);
    }
  };

  const handleCompareBids = async () => {
    if (!selectedTender) {
      showError('Please select a tender');
      return;
    }

    setLoading(true);
    try {
      const response = await api.get(`/api/v1/tenders/${selectedTender.id}/compare-bids`);
      setComparisonData(response.data);
      setComparisonDialogOpen(true);
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to compare bids');
    } finally {
      setLoading(false);
    }
  };

  const handleAwardTender = async (bidId) => {
    if (!selectedTender) return;
    
    setLoading(true);
    try {
      await api.post(`/api/v1/tenders/${selectedTender.id}/award`, {
        bid_id: bidId,
      });
      showSuccess('Tender awarded successfully');
      fetchTenders();
      fetchBids();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to award tender');
    } finally {
      setLoading(false);
    }
  };

  const renderTendersTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Tenders</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setTenderDialogOpen(true)}
        >
          Create Tender
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Tender Number</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Estimated Value</TableCell>
              <TableCell>Issue Date</TableCell>
              <TableCell>Last Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tenders.map((tender) => (
              <TableRow key={tender.id}>
                <TableCell>{tender.tender_number}</TableCell>
                <TableCell>{tender.title}</TableCell>
                <TableCell>
                  <Chip label={tender.tender_type} size="small" />
                </TableCell>
                <TableCell>₹{tender.estimated_value.toLocaleString()}</TableCell>
                <TableCell>{new Date(tender.tender_issue_date).toLocaleDateString()}</TableCell>
                <TableCell>{new Date(tender.last_date_submission).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Chip
                    label={tender.status}
                    color={
                      tender.status === 'published' ? 'success' :
                      tender.status === 'awarded' ? 'primary' :
                      tender.status === 'closed' ? 'default' : 'warning'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedTender(tender);
                      setActiveTab(1);
                    }}
                  >
                    <DescriptionIcon />
                  </IconButton>
                  {tender.status === 'draft' && (
                    <IconButton
                      size="small"
                      color="success"
                      onClick={() => handlePublishTender(tender.id)}
                    >
                      <CheckCircleIcon />
                    </IconButton>
                  )}
                  <IconButton
                    size="small"
                    onClick={() => {
                      setSelectedTender(tender);
                      setIsBidDocument(false);
                      setDocumentDialogOpen(true);
                    }}
                  >
                    <UploadFileIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={tenderDialogOpen} onClose={() => setTenderDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Tender</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Title"
              value={tenderForm.title}
              onChange={(e) => setTenderForm({ ...tenderForm, title: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={tenderForm.description}
              onChange={(e) => setTenderForm({ ...tenderForm, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
            <TextField
              select
              label="Tender Type"
              value={tenderForm.tender_type}
              onChange={(e) => setTenderForm({ ...tenderForm, tender_type: e.target.value })}
              fullWidth
              required
            >
              <MenuItem value="asset_procurement">Asset Procurement</MenuItem>
              <MenuItem value="inventory_purchase">Inventory Purchase</MenuItem>
              <MenuItem value="construction">Construction</MenuItem>
              <MenuItem value="service">Service</MenuItem>
            </TextField>
            <TextField
              label="Estimated Value"
              type="number"
              value={tenderForm.estimated_value}
              onChange={(e) => setTenderForm({ ...tenderForm, estimated_value: parseFloat(e.target.value) || 0 })}
              fullWidth
            />
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Issue Date"
                    value={tenderForm.tender_issue_date}
                    onChange={(date) => setTenderForm({ ...tenderForm, tender_issue_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Last Date"
                    value={tenderForm.last_date_submission}
                    onChange={(date) => setTenderForm({ ...tenderForm, last_date_submission: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Opening Date"
                    value={tenderForm.opening_date}
                    onChange={(date) => setTenderForm({ ...tenderForm, opening_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
            </Grid>
            <TextField
              label="Terms & Conditions"
              value={tenderForm.terms_conditions}
              onChange={(e) => setTenderForm({ ...tenderForm, terms_conditions: e.target.value })}
              fullWidth
              multiline
              rows={4}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTenderDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateTender} variant="contained" disabled={loading}>
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  const renderBidsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">
          Bids {selectedTender && `- ${selectedTender.title}`}
        </Typography>
        <Stack direction="row" spacing={2}>
          {selectedTender && bids.length > 1 && (
            <Button
              variant="outlined"
              startIcon={<CompareArrowsIcon />}
              onClick={handleCompareBids}
            >
              Compare Bids
            </Button>
          )}
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setBidDialogOpen(true)}
            disabled={!selectedTender}
          >
            Submit Bid
          </Button>
        </Stack>
      </Box>

      {!selectedTender && (
        <Alert severity="info">
          Please select a tender from the Tenders tab to view bids
        </Alert>
      )}

      {selectedTender && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Vendor</TableCell>
                <TableCell>Bid Amount</TableCell>
                <TableCell>Bid Date</TableCell>
                <TableCell>Technical Score</TableCell>
                <TableCell>Financial Score</TableCell>
                <TableCell>Total Score</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {bids.map((bid) => (
                <TableRow key={bid.id}>
                  <TableCell>{bid.vendor_name}</TableCell>
                  <TableCell>₹{bid.bid_amount.toLocaleString()}</TableCell>
                  <TableCell>{new Date(bid.bid_date).toLocaleDateString()}</TableCell>
                  <TableCell>{bid.technical_score || '-'}</TableCell>
                  <TableCell>{bid.financial_score || '-'}</TableCell>
                  <TableCell>
                    {bid.total_score ? (
                      <Chip label={bid.total_score.toFixed(2)} color="primary" size="small" />
                    ) : (
                      '-'
                    )}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={bid.status}
                      color={
                        bid.status === 'awarded' ? 'success' :
                        bid.status === 'rejected' ? 'error' :
                        bid.status === 'shortlisted' ? 'warning' : 'default'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => {
                        setSelectedBid(bid);
                        setIsBidDocument(true);
                        setDocumentDialogOpen(true);
                      }}
                    >
                      <UploadFileIcon />
                    </IconButton>
                    {selectedTender.status === 'published' && bid.status === 'submitted' && (
                      <IconButton
                        size="small"
                        color="success"
                        onClick={() => handleAwardTender(bid.id)}
                      >
                        <GavelIcon />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={bidDialogOpen} onClose={() => setBidDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Submit Bid</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              select
              label="Vendor"
              value={bidForm.vendor_id}
              onChange={(e) => setBidForm({ ...bidForm, vendor_id: e.target.value })}
              fullWidth
              required
            >
              {vendors.map((vendor) => (
                <MenuItem key={vendor.id} value={vendor.id}>
                  {vendor.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Bid Amount"
              type="number"
              value={bidForm.bid_amount}
              onChange={(e) => setBidForm({ ...bidForm, bid_amount: parseFloat(e.target.value) || 0 })}
              fullWidth
              required
            />
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Bid Date"
                value={bidForm.bid_date}
                onChange={(date) => setBidForm({ ...bidForm, bid_date: date })}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </LocalizationProvider>
            <TextField
              label="Validity Period (Days)"
              type="number"
              value={bidForm.validity_period_days}
              onChange={(e) => setBidForm({ ...bidForm, validity_period_days: parseInt(e.target.value) || 90 })}
              fullWidth
            />
            <TextField
              label="Technical Specifications"
              value={bidForm.technical_specifications}
              onChange={(e) => setBidForm({ ...bidForm, technical_specifications: e.target.value })}
              fullWidth
              multiline
              rows={3}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBidDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmitBid} variant="contained" disabled={loading}>
            Submit Bid
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={comparisonDialogOpen} onClose={() => setComparisonDialogOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Bid Comparison</DialogTitle>
        <DialogContent>
          {comparisonData && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">Total Bids</Typography>
                      <Typography variant="h4">{comparisonData.total_bids}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">Lowest Bid</Typography>
                      <Typography variant="h4">₹{comparisonData.lowest_bid?.toLocaleString() || '-'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={4}>
                  <Card>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">Average Bid</Typography>
                      <Typography variant="h4">₹{comparisonData.average_bid?.toLocaleString() || '-'}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Bid Amount</TableCell>
                      <TableCell>Variance from Avg</TableCell>
                      <TableCell>Score Rank</TableCell>
                      <TableCell>Total Score</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {comparisonData.bids?.map((bid, index) => (
                      <TableRow key={bid.bid_id}>
                        <TableCell>{bid.vendor_name}</TableCell>
                        <TableCell>₹{bid.bid_amount.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={`${bid.variance_from_average > 0 ? '+' : ''}${bid.variance_from_average.toFixed(2)}%`}
                            color={bid.variance_from_average < 0 ? 'success' : 'warning'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip label={`#${bid.score_rank || index + 1}`} color="primary" size="small" />
                        </TableCell>
                        <TableCell>{bid.total_score?.toFixed(2) || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComparisonDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Tender Management
        </Typography>

        <Paper sx={{ mt: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<DescriptionIcon />} iconPosition="start" label="Tenders" />
            <Tab icon={<AssessmentIcon />} iconPosition="start" label="Bids" />
          </Tabs>

          <Box sx={{ p: 3 }}>
            {loading && (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </Box>
            )}

            {!loading && activeTab === 0 && renderTendersTab()}
            {!loading && activeTab === 1 && renderBidsTab()}
          </Box>
        </Paper>

        <Dialog open={documentDialogOpen} onClose={() => setDocumentDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>
            {isBidDocument ? 'Upload Bid Document' : 'Upload Tender Document'}
          </DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ mt: 1 }}>
              <TextField
                select
                label="Document Type"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                fullWidth
              >
                <MenuItem value="tender">Tender Document</MenuItem>
                <MenuItem value="specification">Specification</MenuItem>
                <MenuItem value="terms">Terms & Conditions</MenuItem>
                <MenuItem value="bid">Bid Document</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </TextField>
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
      </Container>
    </Layout>
  );
};

export default TenderManagement;

