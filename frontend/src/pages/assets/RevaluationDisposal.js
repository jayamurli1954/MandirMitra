import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import DeleteIcon from '@mui/icons-material/Delete';
import Layout from '../../components/Layout';
import api from '../../services/api';
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

const RevaluationDisposal = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [assets, setAssets] = useState([]);
  const [revaluations, setRevaluations] = useState([]);
  const [disposals, setDisposals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [revaluationDialogOpen, setRevaluationDialogOpen] = useState(false);
  const [disposalDialogOpen, setDisposalDialogOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);

  const [revaluationForm, setRevaluationForm] = useState({
    asset_id: '',
    revaluation_date: new Date(),
    revaluation_type: 'INCREASE',
    revalued_amount: 0,
    valuation_method: 'PROFESSIONAL_VALUER',
    valuer_name: '',
    valuation_report_number: '',
    valuation_report_date: null,
  });

  const [disposalForm, setDisposalForm] = useState({
    asset_id: '',
    disposal_date: new Date(),
    disposal_type: 'sale',
    disposal_reason: '',
    disposal_proceeds: 0,
    buyer_name: '',
    disposal_document_number: '',
  });

  useEffect(() => {
    fetchAssets();
  }, []);

  useEffect(() => {
    if (selectedAsset && activeTab === 0) {
      fetchRevaluations();
    } else if (selectedAsset && activeTab === 1) {
      fetchDisposals();
    }
  }, [selectedAsset, activeTab]);

  const fetchAssets = async () => {
    try {
      const response = await api.get('/api/v1/assets/');
      setAssets(response.data.filter(a => a.status === 'active'));
    } catch (err) {
      setError('Failed to load assets');
    }
  };

  const fetchRevaluations = async () => {
    if (!selectedAsset) return;
    try {
      const response = await api.get(`/api/v1/assets/revaluation/${selectedAsset.id}`);
      setRevaluations(response.data || []);
    } catch (err) {
      console.error('Error fetching revaluations:', err);
    }
  };

  const fetchDisposals = async () => {
    if (!selectedAsset) return;
    try {
      const response = await api.get(`/api/v1/assets/disposal/${selectedAsset.id}`);
      setDisposals(response.data || []);
    } catch (err) {
      console.error('Error fetching disposals:', err);
    }
  };

  const handleRevaluationSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const requestData = {
        ...revaluationForm,
        revaluation_date: revaluationForm.revaluation_date.toISOString().split('T')[0],
        valuation_report_date: revaluationForm.valuation_report_date ? revaluationForm.valuation_report_date.toISOString().split('T')[0] : null,
        revalued_amount: parseFloat(revaluationForm.revalued_amount),
      };

      await api.post(`/api/v1/assets/revaluation/?asset_id=${revaluationForm.asset_id}`, requestData);
      setSuccess('Revaluation recorded successfully');
      setRevaluationDialogOpen(false);
      fetchAssets();
      fetchRevaluations();
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record revaluation');
    }
  };

  const handleDisposalSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const requestData = {
        ...disposalForm,
        disposal_date: disposalForm.disposal_date.toISOString().split('T')[0],
        disposal_proceeds: parseFloat(disposalForm.disposal_proceeds),
      };

      await api.post(`/api/v1/assets/disposal/?asset_id=${disposalForm.asset_id}`, requestData);
      setSuccess('Asset disposal recorded successfully');
      setDisposalDialogOpen(false);
      fetchAssets();
      fetchDisposals();
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record disposal');
    }
  };

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Revaluation & Disposal
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<TrendingUpIcon />}
              onClick={() => {
                setSelectedAsset(null);
                setRevaluationForm({
                  asset_id: '',
                  revaluation_date: new Date(),
                  revaluation_type: 'INCREASE',
                  revalued_amount: 0,
                  valuation_method: 'PROFESSIONAL_VALUER',
                  valuer_name: '',
                  valuation_report_number: '',
                  valuation_report_date: null,
                });
                setRevaluationDialogOpen(true);
              }}
            >
              Revalue Asset
            </Button>
            <Button
              variant="contained"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => {
                setSelectedAsset(null);
                setDisposalForm({
                  asset_id: '',
                  disposal_date: new Date(),
                  disposal_type: 'sale',
                  disposal_reason: '',
                  disposal_proceeds: 0,
                  buyer_name: '',
                  disposal_document_number: '',
                });
                setDisposalDialogOpen(true);
              }}
            >
              Dispose Asset
            </Button>
          </Box>
        </Box>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>{success}</Alert>}

        <Paper>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Revaluation History" />
            <Tab label="Disposal History" />
          </Tabs>

          {/* Revaluation Tab */}
          <TabPanel value={activeTab} index={0}>
            <Box sx={{ p: 2 }}>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Select Asset"
                    value={selectedAsset?.id || ''}
                    onChange={(e) => {
                      const asset = assets.find(a => a.id === parseInt(e.target.value));
                      setSelectedAsset(asset);
                    }}
                  >
                    <MenuItem value="">All Assets</MenuItem>
                    {assets.map((asset) => (
                      <MenuItem key={asset.id} value={asset.id}>
                        {asset.asset_number} - {asset.name}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Asset</TableCell>
                      <TableCell>Revaluation Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Previous Value</TableCell>
                      <TableCell>Revalued Amount</TableCell>
                      <TableCell>Change</TableCell>
                      <TableCell>Valuer</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {revaluations.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                          <Typography variant="body2" color="text.secondary">
                            {selectedAsset ? 'No revaluations found for this asset' : 'Select an asset to view revaluation history'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      revaluations.map((reval) => (
                        <TableRow key={reval.id}>
                          <TableCell>{selectedAsset?.name || 'N/A'}</TableCell>
                          <TableCell>{new Date(reval.revaluation_date).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Chip
                              label={reval.revaluation_type}
                              size="small"
                              color={reval.revaluation_type === 'INCREASE' ? 'success' : 'error'}
                            />
                          </TableCell>
                          <TableCell>₹{reval.previous_book_value?.toLocaleString() || 0}</TableCell>
                          <TableCell>₹{reval.revalued_amount?.toLocaleString() || 0}</TableCell>
                          <TableCell>
                            <Typography
                              color={reval.revaluation_amount >= 0 ? 'success.main' : 'error.main'}
                            >
                              {reval.revaluation_amount >= 0 ? '+' : ''}₹{reval.revaluation_amount?.toLocaleString() || 0}
                            </Typography>
                          </TableCell>
                          <TableCell>{reval.valuer_name || 'N/A'}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </TabPanel>

          {/* Disposal Tab */}
          <TabPanel value={activeTab} index={1}>
            <Box sx={{ p: 2 }}>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Select Asset"
                    value={selectedAsset?.id || ''}
                    onChange={(e) => {
                      const asset = assets.find(a => a.id === parseInt(e.target.value));
                      setSelectedAsset(asset);
                    }}
                  >
                    <MenuItem value="">All Assets</MenuItem>
                    {assets.map((asset) => (
                      <MenuItem key={asset.id} value={asset.id}>
                        {asset.asset_number} - {asset.name}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
              </Grid>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Asset</TableCell>
                      <TableCell>Disposal Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Book Value</TableCell>
                      <TableCell>Proceeds</TableCell>
                      <TableCell>Gain/Loss</TableCell>
                      <TableCell>Buyer</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {disposals.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                          <Typography variant="body2" color="text.secondary">
                            {selectedAsset ? 'No disposals found for this asset' : 'Select an asset to view disposal history'}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      disposals.map((disposal) => (
                        <TableRow key={disposal.id}>
                          <TableCell>{selectedAsset?.name || 'N/A'}</TableCell>
                          <TableCell>{new Date(disposal.disposal_date).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Chip label={disposal.disposal_type} size="small" />
                          </TableCell>
                          <TableCell>₹{disposal.book_value_at_disposal?.toLocaleString() || 0}</TableCell>
                          <TableCell>₹{disposal.disposal_proceeds?.toLocaleString() || 0}</TableCell>
                          <TableCell>
                            <Typography
                              color={disposal.gain_loss_amount >= 0 ? 'success.main' : 'error.main'}
                            >
                              {disposal.gain_loss_amount >= 0 ? 'Gain: ' : 'Loss: '}₹{Math.abs(disposal.gain_loss_amount)?.toLocaleString() || 0}
                            </Typography>
                          </TableCell>
                          <TableCell>{disposal.buyer_name || 'N/A'}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          </TabPanel>
        </Paper>

        {/* Revaluation Dialog */}
        <Dialog open={revaluationDialogOpen} onClose={() => setRevaluationDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handleRevaluationSubmit}>
            <DialogTitle>Revalue Asset</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    select
                    label="Asset *"
                    value={revaluationForm.asset_id}
                    onChange={(e) => setRevaluationForm({ ...revaluationForm, asset_id: e.target.value })}
                    required
                  >
                    {assets.map((asset) => (
                      <MenuItem key={asset.id} value={asset.id}>
                        {asset.asset_number} - {asset.name} (Book Value: ₹{asset.current_book_value?.toLocaleString() || 0})
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Revaluation Date *"
                      value={revaluationForm.revaluation_date}
                      onChange={(newValue) => setRevaluationForm({ ...revaluationForm, revaluation_date: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth required />}
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Revaluation Type *"
                    value={revaluationForm.revaluation_type}
                    onChange={(e) => setRevaluationForm({ ...revaluationForm, revaluation_type: e.target.value })}
                    required
                  >
                    <MenuItem value="INCREASE">Increase</MenuItem>
                    <MenuItem value="DECREASE">Decrease</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Revalued Amount *"
                    value={revaluationForm.revalued_amount}
                    onChange={(e) => setRevaluationForm({ ...revaluationForm, revalued_amount: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Valuation Method"
                    value={revaluationForm.valuation_method}
                    onChange={(e) => setRevaluationForm({ ...revaluationForm, valuation_method: e.target.value })}
                  >
                    <MenuItem value="MARKET_VALUE">Market Value</MenuItem>
                    <MenuItem value="PROFESSIONAL_VALUER">Professional Valuer</MenuItem>
                    <MenuItem value="INDEX_BASED">Index Based</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Valuer Name"
                    value={revaluationForm.valuer_name}
                    onChange={(e) => setRevaluationForm({ ...revaluationForm, valuer_name: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Valuation Report Number"
                    value={revaluationForm.valuation_report_number}
                    onChange={(e) => setRevaluationForm({ ...revaluationForm, valuation_report_number: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Valuation Report Date"
                      value={revaluationForm.valuation_report_date}
                      onChange={(newValue) => setRevaluationForm({ ...revaluationForm, valuation_report_date: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth />}
                    />
                  </LocalizationProvider>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setRevaluationDialogOpen(false)}>Cancel</Button>
              <Button type="submit" variant="contained">Record Revaluation</Button>
            </DialogActions>
          </form>
        </Dialog>

        {/* Disposal Dialog */}
        <Dialog open={disposalDialogOpen} onClose={() => setDisposalDialogOpen(false)} maxWidth="sm" fullWidth>
          <form onSubmit={handleDisposalSubmit}>
            <DialogTitle>Dispose Asset</DialogTitle>
            <DialogContent>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    select
                    label="Asset *"
                    value={disposalForm.asset_id}
                    onChange={(e) => {
                      const asset = assets.find(a => a.id === parseInt(e.target.value));
                      setDisposalForm({ ...disposalForm, asset_id: e.target.value });
                      if (asset) {
                        setDisposalForm(prev => ({
                          ...prev,
                          disposal_proceeds: asset.current_book_value || 0
                        }));
                      }
                    }}
                    required
                  >
                    {assets.map((asset) => (
                      <MenuItem key={asset.id} value={asset.id}>
                        {asset.asset_number} - {asset.name} (Book Value: ₹{asset.current_book_value?.toLocaleString() || 0})
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <LocalizationProvider dateAdapter={AdapterDateFns}>
                    <DatePicker
                      label="Disposal Date *"
                      value={disposalForm.disposal_date}
                      onChange={(newValue) => setDisposalForm({ ...disposalForm, disposal_date: newValue })}
                      renderInput={(params) => <TextField {...params} fullWidth required />}
                    />
                  </LocalizationProvider>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    select
                    label="Disposal Type *"
                    value={disposalForm.disposal_type}
                    onChange={(e) => setDisposalForm({ ...disposalForm, disposal_type: e.target.value })}
                    required
                  >
                    <MenuItem value="sale">Sale</MenuItem>
                    <MenuItem value="scrap">Scrap</MenuItem>
                    <MenuItem value="donation">Donation</MenuItem>
                    <MenuItem value="loss">Loss</MenuItem>
                    <MenuItem value="theft">Theft</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Disposal Reason"
                    value={disposalForm.disposal_reason}
                    onChange={(e) => setDisposalForm({ ...disposalForm, disposal_reason: e.target.value })}
                    multiline
                    rows={2}
                  />
                </Grid>
                {disposalForm.disposal_type === 'sale' && (
                  <>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        type="number"
                        label="Sale Proceeds"
                        value={disposalForm.disposal_proceeds}
                        onChange={(e) => setDisposalForm({ ...disposalForm, disposal_proceeds: parseFloat(e.target.value) || 0 })}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Buyer Name"
                        value={disposalForm.buyer_name}
                        onChange={(e) => setDisposalForm({ ...disposalForm, buyer_name: e.target.value })}
                      />
                    </Grid>
                  </>
                )}
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Document Number"
                    value={disposalForm.disposal_document_number}
                    onChange={(e) => setDisposalForm({ ...disposalForm, disposal_document_number: e.target.value })}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDisposalDialogOpen(false)}>Cancel</Button>
              <Button type="submit" variant="contained" color="error">Record Disposal</Button>
            </DialogActions>
          </form>
        </Dialog>
      </Container>
    </Layout>
  );
};

export default RevaluationDisposal;

