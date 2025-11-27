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
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
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

const AssetReportsPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Asset Register
  const [assetRegister, setAssetRegister] = useState(null);
  const [registerFilters, setRegisterFilters] = useState({
    category_id: '',
    asset_type: '',
    status: '',
  });

  // Depreciation Report
  const [depreciationReport, setDepreciationReport] = useState(null);
  const [depreciationFilters, setDepreciationFilters] = useState({
    financial_year: `${new Date().getFullYear()}-${String(new Date().getFullYear() + 1).slice(-2)}`,
    period: '',
    asset_id: '',
  });

  // CWIP Report
  const [cwipReport, setCwipReport] = useState(null);
  const [cwipStatusFilter, setCwipStatusFilter] = useState('');

  // Summary
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetchSummary();
  }, []);

  useEffect(() => {
    if (activeTab === 0) {
      fetchAssetRegister();
    } else if (activeTab === 1) {
      fetchDepreciationReport();
    } else if (activeTab === 2) {
      fetchCWIPReport();
    }
  }, [activeTab, registerFilters, depreciationFilters, cwipStatusFilter]);

  const fetchSummary = async () => {
    try {
      const response = await api.get('/api/v1/assets/reports/summary/');
      setSummary(response.data);
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  const fetchAssetRegister = async () => {
    try {
      setLoading(true);
      const params = {};
      if (registerFilters.category_id) params.category_id = registerFilters.category_id;
      if (registerFilters.asset_type) params.asset_type = registerFilters.asset_type;
      if (registerFilters.status) params.status = registerFilters.status;

      const response = await api.get('/api/v1/assets/reports/register/', { params });
      setAssetRegister(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load asset register');
    } finally {
      setLoading(false);
    }
  };

  const fetchDepreciationReport = async () => {
    try {
      setLoading(true);
      const params = {
        financial_year: depreciationFilters.financial_year,
      };
      if (depreciationFilters.period) params.period = depreciationFilters.period;
      if (depreciationFilters.asset_id) params.asset_id = depreciationFilters.asset_id;

      const response = await api.get('/api/v1/assets/reports/depreciation/', { params });
      setDepreciationReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load depreciation report');
    } finally {
      setLoading(false);
    }
  };

  const fetchCWIPReport = async () => {
    try {
      setLoading(true);
      const params = {};
      if (cwipStatusFilter) params.status = cwipStatusFilter;

      const response = await api.get('/api/v1/assets/reports/cwip/', { params });
      setCwipReport(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load CWIP report');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (data, filename) => {
    // Simple CSV export
    if (!data || !data.assets) return;
    
    const headers = ['Asset Number', 'Name', 'Category', 'Type', 'Cost', 'Book Value', 'Depreciation', 'Status'];
    const rows = data.assets.map(asset => [
      asset.asset_number,
      asset.name,
      asset.category,
      asset.asset_type,
      asset.original_cost,
      asset.current_book_value,
      asset.accumulated_depreciation,
      asset.status,
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  };

  return (
    <Layout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
          Asset Reports
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

        {/* Summary Cards */}
        {summary && (
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e3f2fd' }}>
                <Typography variant="h6">{summary.total_assets}</Typography>
                <Typography variant="body2">Total Assets</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#f3e5f5' }}>
                <Typography variant="h6">₹{summary.total_cost?.toLocaleString() || 0}</Typography>
                <Typography variant="body2">Total Cost</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#fff3e0' }}>
                <Typography variant="h6">₹{summary.total_book_value?.toLocaleString() || 0}</Typography>
                <Typography variant="body2">Book Value</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: '#e8f5e9' }}>
                <Typography variant="h6">{summary.active_cwip_projects || 0}</Typography>
                <Typography variant="body2">Active CWIP</Typography>
              </Paper>
            </Grid>
          </Grid>
        )}

        <Paper>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Asset Register" />
            <Tab label="Depreciation Report" />
            <Tab label="CWIP Report" />
          </Tabs>

          {/* Asset Register Tab */}
          <TabPanel value={activeTab} index={0}>
            <Box sx={{ p: 2 }}>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Asset Type"
                    value={registerFilters.asset_type}
                    onChange={(e) => setRegisterFilters({ ...registerFilters, asset_type: e.target.value })}
                    size="small"
                  >
                    <MenuItem value="">All Types</MenuItem>
                    <MenuItem value="fixed">Fixed</MenuItem>
                    <MenuItem value="movable">Movable</MenuItem>
                    <MenuItem value="precious">Precious</MenuItem>
                    <MenuItem value="intangible">Intangible</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Status"
                    value={registerFilters.status}
                    onChange={(e) => setRegisterFilters({ ...registerFilters, status: e.target.value })}
                    size="small"
                  >
                    <MenuItem value="">All Status</MenuItem>
                    <MenuItem value="active">Active</MenuItem>
                    <MenuItem value="disposed">Disposed</MenuItem>
                    <MenuItem value="sold">Sold</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleExport(assetRegister, 'asset-register.csv')}
                    disabled={!assetRegister}
                  >
                    Export
                  </Button>
                </Grid>
              </Grid>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : assetRegister ? (
                <>
                  <Box sx={{ mb: 2, p: 2, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body2">
                      Total Assets: {assetRegister.total_assets} | 
                      Total Cost: ₹{assetRegister.total_cost?.toLocaleString() || 0} | 
                      Book Value: ₹{assetRegister.total_book_value?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Asset Number</TableCell>
                          <TableCell>Name</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell>Type</TableCell>
                          <TableCell align="right">Cost</TableCell>
                          <TableCell align="right">Book Value</TableCell>
                          <TableCell align="right">Depreciation</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {assetRegister.assets.map((asset) => (
                          <TableRow key={asset.asset_id}>
                            <TableCell>{asset.asset_number}</TableCell>
                            <TableCell>{asset.name}</TableCell>
                            <TableCell>{asset.category}</TableCell>
                            <TableCell>
                              <Chip label={asset.asset_type} size="small" />
                            </TableCell>
                            <TableCell align="right">₹{asset.original_cost?.toLocaleString() || 0}</TableCell>
                            <TableCell align="right">₹{asset.current_book_value?.toLocaleString() || 0}</TableCell>
                            <TableCell align="right">₹{asset.accumulated_depreciation?.toLocaleString() || 0}</TableCell>
                            <TableCell>
                              <Chip label={asset.status} size="small" color={asset.status === 'active' ? 'success' : 'default'} />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              ) : null}
            </Box>
          </TabPanel>

          {/* Depreciation Report Tab */}
          <TabPanel value={activeTab} index={1}>
            <Box sx={{ p: 2 }}>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Financial Year"
                    value={depreciationFilters.financial_year}
                    onChange={(e) => setDepreciationFilters({ ...depreciationFilters, financial_year: e.target.value })}
                    size="small"
                    placeholder="2024-25"
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Period"
                    value={depreciationFilters.period}
                    onChange={(e) => setDepreciationFilters({ ...depreciationFilters, period: e.target.value })}
                    size="small"
                  >
                    <MenuItem value="">All Periods</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                    <MenuItem value="yearly">Yearly</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    variant="contained"
                    onClick={fetchDepreciationReport}
                    disabled={loading}
                  >
                    Generate Report
                  </Button>
                </Grid>
              </Grid>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : depreciationReport ? (
                <>
                  <Box sx={{ mb: 2, p: 2, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body2">
                      Total Depreciation: ₹{depreciationReport.total_depreciation?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Asset</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell>Method</TableCell>
                          <TableCell>Financial Year</TableCell>
                          <TableCell>Period</TableCell>
                          <TableCell align="right">Opening Value</TableCell>
                          <TableCell align="right">Depreciation</TableCell>
                          <TableCell align="right">Closing Value</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {depreciationReport.schedules.map((schedule) => (
                          <TableRow key={schedule.asset_id + schedule.period}>
                            <TableCell>{schedule.asset_name}</TableCell>
                            <TableCell>{schedule.category}</TableCell>
                            <TableCell>{schedule.depreciation_method}</TableCell>
                            <TableCell>{schedule.financial_year}</TableCell>
                            <TableCell>{schedule.period}</TableCell>
                            <TableCell align="right">₹{schedule.opening_book_value?.toLocaleString() || 0}</TableCell>
                            <TableCell align="right">₹{schedule.depreciation_amount?.toLocaleString() || 0}</TableCell>
                            <TableCell align="right">₹{schedule.closing_book_value?.toLocaleString() || 0}</TableCell>
                            <TableCell>
                              <Chip label={schedule.status} size="small" color={schedule.status === 'posted' ? 'success' : 'warning'} />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              ) : null}
            </Box>
          </TabPanel>

          {/* CWIP Report Tab */}
          <TabPanel value={activeTab} index={2}>
            <Box sx={{ p: 2 }}>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Status"
                    value={cwipStatusFilter}
                    onChange={(e) => setCwipStatusFilter(e.target.value)}
                    size="small"
                  >
                    <MenuItem value="">All Status</MenuItem>
                    <MenuItem value="in_progress">In Progress</MenuItem>
                    <MenuItem value="completed">Completed</MenuItem>
                    <MenuItem value="suspended">Suspended</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    variant="contained"
                    onClick={fetchCWIPReport}
                    disabled={loading}
                  >
                    Generate Report
                  </Button>
                </Grid>
              </Grid>

              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : cwipReport ? (
                <>
                  <Box sx={{ mb: 2, p: 2, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body2">
                      Total Projects: {cwipReport.total_projects} | 
                      Total Budget: ₹{cwipReport.total_budget?.toLocaleString() || 0} | 
                      Total Expenditure: ₹{cwipReport.total_expenditure?.toLocaleString() || 0}
                    </Typography>
                  </Box>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>CWIP Number</TableCell>
                          <TableCell>Project Name</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell>Start Date</TableCell>
                          <TableCell>Expected Completion</TableCell>
                          <TableCell align="right">Budget</TableCell>
                          <TableCell align="right">Expenditure</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {cwipReport.projects.map((project) => (
                          <TableRow key={project.cwip_id}>
                            <TableCell>{project.cwip_number}</TableCell>
                            <TableCell>{project.project_name}</TableCell>
                            <TableCell>{project.category}</TableCell>
                            <TableCell>{new Date(project.start_date).toLocaleDateString()}</TableCell>
                            <TableCell>{project.expected_completion_date ? new Date(project.expected_completion_date).toLocaleDateString() : 'N/A'}</TableCell>
                            <TableCell align="right">₹{project.total_budget?.toLocaleString() || 0}</TableCell>
                            <TableCell align="right">₹{project.total_expenditure?.toLocaleString() || 0}</TableCell>
                            <TableCell>
                              <Chip label={project.status} size="small" color={project.status === 'completed' ? 'success' : 'default'} />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              ) : null}
            </Box>
          </TabPanel>
        </Paper>
      </Container>
    </Layout>
  );
};

export default AssetReportsPage;


