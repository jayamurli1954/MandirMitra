import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  IconButton,
  Alert,
  CircularProgress,
  MenuItem,
  Chip,
  Tabs,
  Tab,
  Card,
  CardContent
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PublishIcon from '@mui/icons-material/Publish';
import CloseIcon from '@mui/icons-material/Close';
import axios from 'axios';
import { format } from 'date-fns';

const TenderManagement = () => {
  const [tenders, setTenders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [selectedTender, setSelectedTender] = useState(null);
  const [editingTender, setEditingTender] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    tender_type: 'ASSET_PROCUREMENT',
    estimated_value: '',
    tender_issue_date: new Date(),
    last_date_submission: new Date(),
    opening_date: null,
    terms_conditions: ''
  });

  useEffect(() => {
    fetchTenders();
  }, [tabValue]);

  const fetchTenders = async () => {
    setLoading(true);
    try {
      let url = '/api/v1/tenders/';
      if (tabValue === 1) {
        url += '?status=draft';
      } else if (tabValue === 2) {
        url += '?status=published';
      } else if (tabValue === 3) {
        url += '?status=closed';
      } else if (tabValue === 4) {
        url += '?status=awarded';
      }
      
      const response = await axios.get(url);
      setTenders(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load tenders');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (tender = null) => {
    if (tender) {
      setEditingTender(tender);
      setFormData({
        title: tender.title || '',
        description: tender.description || '',
        tender_type: tender.tender_type || 'ASSET_PROCUREMENT',
        estimated_value: tender.estimated_value || '',
        tender_issue_date: tender.tender_issue_date ? new Date(tender.tender_issue_date) : new Date(),
        last_date_submission: tender.last_date_submission ? new Date(tender.last_date_submission) : new Date(),
        opening_date: tender.opening_date ? new Date(tender.opening_date) : null,
        terms_conditions: tender.terms_conditions || ''
      });
    } else {
      setEditingTender(null);
      setFormData({
        title: '',
        description: '',
        tender_type: 'ASSET_PROCUREMENT',
        estimated_value: '',
        tender_issue_date: new Date(),
        last_date_submission: new Date(),
        opening_date: null,
        terms_conditions: ''
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingTender(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      const payload = {
        ...formData,
        tender_issue_date: format(formData.tender_issue_date, 'yyyy-MM-dd'),
        last_date_submission: format(formData.last_date_submission, 'yyyy-MM-dd'),
        opening_date: formData.opening_date ? format(formData.opening_date, 'yyyy-MM-dd') : null,
        estimated_value: formData.estimated_value ? parseFloat(formData.estimated_value) : null
      };
      
      if (editingTender) {
        await axios.put(`/api/v1/tenders/${editingTender.id}`, payload);
        setSuccess('Tender updated successfully');
      } else {
        await axios.post('/api/v1/tenders/', payload);
        setSuccess('Tender created successfully');
      }
      
      handleCloseDialog();
      fetchTenders();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save tender');
    }
  };

  const handlePublish = async (tenderId) => {
    try {
      await axios.post(`/api/v1/tenders/${tenderId}/publish`);
      setSuccess('Tender published successfully');
      fetchTenders();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to publish tender');
    }
  };

  const handleClose = async (tenderId) => {
    try {
      await axios.post(`/api/v1/tenders/${tenderId}/close`);
      setSuccess('Tender closed successfully');
      fetchTenders();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to close tender');
    }
  };

  const handleViewDetails = async (tender) => {
    try {
      const response = await axios.get(`/api/v1/tenders/${tender.id}`);
      setSelectedTender(response.data);
      setDetailDialogOpen(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load tender details');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'draft': return 'default';
      case 'published': return 'primary';
      case 'closed': return 'warning';
      case 'awarded': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Tender Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create Tender
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="All Tenders" />
          <Tab label="Draft" />
          <Tab label="Published" />
          <Tab label="Closed" />
          <Tab label="Awarded" />
        </Tabs>
      </Paper>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Tender Number</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Estimated Value</TableCell>
                <TableCell>Issue Date</TableCell>
                <TableCell>Submission Deadline</TableCell>
                <TableCell>Bids</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tenders.map((tender) => (
                <TableRow key={tender.id}>
                  <TableCell>{tender.tender_number}</TableCell>
                  <TableCell>{tender.title}</TableCell>
                  <TableCell>{tender.tender_type || 'N/A'}</TableCell>
                  <TableCell>
                    {tender.estimated_value ? `₹${tender.estimated_value.toLocaleString()}` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {tender.tender_issue_date ? format(new Date(tender.tender_issue_date), 'dd-MM-yyyy') : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {tender.last_date_submission ? format(new Date(tender.last_date_submission), 'dd-MM-yyyy') : 'N/A'}
                  </TableCell>
                  <TableCell>{tender.bids_count || 0}</TableCell>
                  <TableCell>
                    <Chip
                      label={tender.status}
                      color={getStatusColor(tender.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleViewDetails(tender)}
                      title="View Details"
                    >
                      <VisibilityIcon />
                    </IconButton>
                    {tender.status === 'draft' && (
                      <>
                        <IconButton
                          size="small"
                          onClick={() => handleOpenDialog(tender)}
                          title="Edit"
                        >
                          <EditIcon />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => handlePublish(tender.id)}
                          title="Publish"
                        >
                          <PublishIcon />
                        </IconButton>
                      </>
                    )}
                    {tender.status === 'published' && (
                      <IconButton
                        size="small"
                        onClick={() => handleClose(tender.id)}
                        title="Close"
                      >
                        <CloseIcon />
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {editingTender ? 'Edit Tender' : 'Create New Tender'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  select
                  label="Tender Type"
                  value={formData.tender_type}
                  onChange={(e) => setFormData({ ...formData, tender_type: e.target.value })}
                >
                  <MenuItem value="ASSET_PROCUREMENT">Asset Procurement</MenuItem>
                  <MenuItem value="INVENTORY_PURCHASE">Inventory Purchase</MenuItem>
                  <MenuItem value="CONSTRUCTION">Construction</MenuItem>
                  <MenuItem value="SERVICE">Service</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Estimated Value (₹)"
                  type="number"
                  value={formData.estimated_value}
                  onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Issue Date"
                    value={formData.tender_issue_date}
                    onChange={(date) => setFormData({ ...formData, tender_issue_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth required />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} sm={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Submission Deadline"
                    value={formData.last_date_submission}
                    onChange={(date) => setFormData({ ...formData, last_date_submission: date })}
                    renderInput={(params) => <TextField {...params} fullWidth required />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12} sm={4}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Opening Date (Optional)"
                    value={formData.opening_date}
                    onChange={(date) => setFormData({ ...formData, opening_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Terms & Conditions"
                  value={formData.terms_conditions}
                  onChange={(e) => setFormData({ ...formData, terms_conditions: e.target.value })}
                  multiline
                  rows={4}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained">
              {editingTender ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Detail Dialog */}
      {selectedTender && (
        <TenderDetailDialog
          open={detailDialogOpen}
          onClose={() => {
            setDetailDialogOpen(false);
            setSelectedTender(null);
          }}
          tender={selectedTender}
          onUpdate={fetchTenders}
        />
      )}
    </Container>
  );
};

// Tender Detail Dialog Component
const TenderDetailDialog = ({ open, onClose, tender, onUpdate }) => {
  const [bids, setBids] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [vendors, setVendors] = useState([]);
  const [bidDialogOpen, setBidDialogOpen] = useState(false);
  const [evaluationDialogOpen, setEvaluationDialogOpen] = useState(false);
  const [selectedBid, setSelectedBid] = useState(null);
  
  const [bidForm, setBidForm] = useState({
    vendor_id: '',
    bid_amount: '',
    bid_date: new Date(),
    validity_period_days: 90,
    technical_specifications: ''
  });

  const [evaluationForm, setEvaluationForm] = useState({
    technical_score: '',
    financial_score: '',
    evaluation_notes: ''
  });

  useEffect(() => {
    if (open && tender) {
      fetchBids();
      fetchVendors();
    }
  }, [open, tender]);

  const fetchBids = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/v1/tenders/${tender.id}/bids`);
      setBids(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load bids');
    } finally {
      setLoading(false);
    }
  };

  const fetchVendors = async () => {
    try {
      const response = await axios.get('/api/v1/vendors/');
      setVendors(response.data);
    } catch (err) {
      console.error('Failed to load vendors:', err);
    }
  };

  const handleSubmitBid = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/v1/tenders/${tender.id}/bids`, {
        ...bidForm,
        tender_id: tender.id,
        bid_date: format(bidForm.bid_date, 'yyyy-MM-dd')
      });
      setBidDialogOpen(false);
      setBidForm({
        vendor_id: '',
        bid_amount: '',
        bid_date: new Date(),
        validity_period_days: 90,
        technical_specifications: ''
      });
      fetchBids();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit bid');
    }
  };

  const handleEvaluateBid = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/v1/tenders/${tender.id}/bids/${selectedBid.id}/evaluate`, {
        bid_id: selectedBid.id,
        ...evaluationForm
      });
      setEvaluationDialogOpen(false);
      setSelectedBid(null);
      fetchBids();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to evaluate bid');
    }
  };

  const handleAwardTender = async (bidId) => {
    if (window.confirm('Are you sure you want to award this tender to the selected bid?')) {
      try {
        await axios.post(`/api/v1/tenders/${tender.id}/award`, {
          bid_id: bidId,
          award_date: format(new Date(), 'yyyy-MM-dd')
        });
        onUpdate();
        onClose();
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to award tender');
      }
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Tender Details: {tender.tender_number}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">Title</Typography>
                <Typography variant="body1">{tender.title}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">Status</Typography>
                <Chip label={tender.status} color="primary" />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">Estimated Value</Typography>
                <Typography variant="body1">
                  {tender.estimated_value ? `₹${tender.estimated_value.toLocaleString()}` : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle2" color="textSecondary">Submission Deadline</Typography>
                <Typography variant="body1">
                  {tender.last_date_submission ? format(new Date(tender.last_date_submission), 'dd-MM-yyyy') : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Bids ({bids.length})</Typography>
          {tender.status === 'published' && (
            <Button
              variant="outlined"
              size="small"
              onClick={() => setBidDialogOpen(true)}
            >
              Add Bid (Manual Entry)
            </Button>
          )}
        </Box>

        {loading ? (
          <CircularProgress />
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Vendor</TableCell>
                  <TableCell>Bid Amount</TableCell>
                  <TableCell>Bid Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Technical Score</TableCell>
                  <TableCell>Financial Score</TableCell>
                  <TableCell>Total Score</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {bids.map((bid) => (
                  <TableRow key={bid.id}>
                    <TableCell>{bid.vendor_name || 'N/A'}</TableCell>
                    <TableCell>₹{bid.bid_amount.toLocaleString()}</TableCell>
                    <TableCell>
                      {bid.bid_date ? format(new Date(bid.bid_date), 'dd-MM-yyyy') : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip label={bid.status} size="small" />
                    </TableCell>
                    <TableCell>{bid.technical_score || '-'}</TableCell>
                    <TableCell>{bid.financial_score || '-'}</TableCell>
                    <TableCell>{bid.total_score ? bid.total_score.toFixed(2) : '-'}</TableCell>
                    <TableCell>
                      {tender.status === 'published' && bid.status === 'submitted' && (
                        <Button
                          size="small"
                          onClick={() => {
                            setSelectedBid(bid);
                            setEvaluationDialogOpen(true);
                          }}
                        >
                          Evaluate
                        </Button>
                      )}
                      {tender.status === 'published' && bid.total_score && (
                        <Button
                          size="small"
                          color="success"
                          onClick={() => handleAwardTender(bid.id)}
                        >
                          Award
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>

      {/* Submit Bid Dialog */}
      <Dialog open={bidDialogOpen} onClose={() => setBidDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmitBid}>
          <DialogTitle>Submit Bid</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  select
                  label="Vendor"
                  value={bidForm.vendor_id}
                  onChange={(e) => setBidForm({ ...bidForm, vendor_id: e.target.value })}
                  required
                >
                  {vendors.map((vendor) => (
                    <MenuItem key={vendor.id} value={vendor.id}>
                      {vendor.name}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Bid Amount (₹)"
                  type="number"
                  value={bidForm.bid_amount}
                  onChange={(e) => setBidForm({ ...bidForm, bid_amount: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <DatePicker
                    label="Bid Date"
                    value={bidForm.bid_date}
                    onChange={(date) => setBidForm({ ...bidForm, bid_date: date })}
                    renderInput={(params) => <TextField {...params} fullWidth required />}
                  />
                </LocalizationProvider>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Validity Period (Days)"
                  type="number"
                  value={bidForm.validity_period_days}
                  onChange={(e) => setBidForm({ ...bidForm, validity_period_days: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Technical Specifications"
                  value={bidForm.technical_specifications}
                  onChange={(e) => setBidForm({ ...bidForm, technical_specifications: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setBidDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Submit</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Evaluation Dialog */}
      <Dialog open={evaluationDialogOpen} onClose={() => setEvaluationDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleEvaluateBid}>
          <DialogTitle>Evaluate Bid</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Technical Score (0-100)"
                  type="number"
                  value={evaluationForm.technical_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, technical_score: e.target.value })}
                  required
                  inputProps={{ min: 0, max: 100 }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Financial Score (0-100)"
                  type="number"
                  value={evaluationForm.financial_score}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, financial_score: e.target.value })}
                  required
                  inputProps={{ min: 0, max: 100 }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Evaluation Notes"
                  value={evaluationForm.evaluation_notes}
                  onChange={(e) => setEvaluationForm({ ...evaluationForm, evaluation_notes: e.target.value })}
                  multiline
                  rows={3}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEvaluationDialogOpen(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Evaluate</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Dialog>
  );
};

export default TenderManagement;

