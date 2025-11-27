import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  IconButton,
  Checkbox,
  FormControlLabel,
  Autocomplete,
  Stack,
} from '@mui/material';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import EditIcon from '@mui/icons-material/Edit';
import MergeIcon from '@mui/icons-material/Merge';
import FamilyRestroomIcon from '@mui/icons-material/FamilyRestroom';
import CakeIcon from '@mui/icons-material/Cake';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import StarIcon from '@mui/icons-material/Star';
import Layout from '../components/Layout';
import api from '../services/api';
import { useNotification } from '../contexts/NotificationContext';

function Devotees() {
  const { showSuccess, showError } = useNotification();
  const [devotees, setDevotees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  const [showVipOnly, setShowVipOnly] = useState(false);
  
  // Dialog states
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [mergeDialogOpen, setMergeDialogOpen] = useState(false);
  const [familyDialogOpen, setFamilyDialogOpen] = useState(false);
  const [tagsDialogOpen, setTagsDialogOpen] = useState(false);
  const [selectedDevotee, setSelectedDevotee] = useState(null);
  const [duplicates, setDuplicates] = useState([]);
  const [upcomingBirthdays, setUpcomingBirthdays] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  
  // Form states
  const [devoteeForm, setDevoteeForm] = useState({
    name: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    country: 'India',
    date_of_birth: '',
    gothra: '',
    nakshatra: '',
    preferred_language: 'en',
    receive_sms: true,
    receive_email: true,
    tags: [],
  });
  
  const [mergeForm, setMergeForm] = useState({
    primary_id: null,
    duplicate_ids: [],
  });
  
  const [familyForm, setFamilyForm] = useState({
    family_head_id: '',
  });
  
  const availableTags = ['VIP', 'Patron', 'Regular', 'NRI', 'Local', 'Festival Donor', 'Monthly Donor'];

  useEffect(() => {
    fetchDevotees();
    if (tabValue === 1) fetchDuplicates();
    if (tabValue === 2) fetchUpcomingBirthdays();
    if (tabValue === 3) fetchAnalytics();
  }, [tabValue, searchTerm, selectedTag, showVipOnly]);
  
  useEffect(() => {
    if (tabValue === 0) {
      fetchDevotees();
    }
  }, [searchTerm, selectedTag, showVipOnly]);

  const fetchDevotees = async () => {
    try {
      setLoading(true);
      setError('');
      
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedTag) params.tag = selectedTag;
      if (showVipOnly) params.is_vip = true;
      
      const response = await api.get('/api/v1/devotees', { params });
      setDevotees(response.data || []);
    } catch (err) {
      console.error('Error fetching devotees:', err);
      setError(err.response?.data?.detail || 'Failed to load devotees');
      setDevotees([]);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchDuplicates = async () => {
    try {
      const response = await api.get('/api/v1/devotees/duplicates');
      setDuplicates(response.data || []);
    } catch (err) {
      console.error('Error fetching duplicates:', err);
    }
  };
  
  const fetchUpcomingBirthdays = async () => {
    try {
      const response = await api.get('/api/v1/devotees/birthdays', { params: { days: 30 } });
      setUpcomingBirthdays(response.data || []);
    } catch (err) {
      console.error('Error fetching birthdays:', err);
    }
  };
  
  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/api/v1/devotees/analytics');
      setAnalytics(response.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  };
  
  const handleEdit = (devotee) => {
    setSelectedDevotee(devotee);
    setDevoteeForm({
      name: devotee.name || '',
      phone: devotee.phone || '',
      email: devotee.email || '',
      address: devotee.address || '',
      city: devotee.city || '',
      state: devotee.state || '',
      pincode: devotee.pincode || '',
      country: devotee.country || 'India',
      date_of_birth: devotee.date_of_birth || '',
      gothra: devotee.gothra || '',
      nakshatra: devotee.nakshatra || '',
      preferred_language: devotee.preferred_language || 'en',
      receive_sms: devotee.receive_sms !== undefined ? devotee.receive_sms : true,
      receive_email: devotee.receive_email !== undefined ? devotee.receive_email : true,
      tags: devotee.tags || [],
    });
    setEditDialogOpen(true);
  };
  
  const handleSaveDevotee = async () => {
    try {
      if (selectedDevotee) {
        await api.put(`/api/v1/devotees/${selectedDevotee.id}`, devoteeForm);
        showSuccess('Devotee updated successfully');
      } else {
        await api.post('/api/v1/devotees', devoteeForm);
        showSuccess('Devotee created successfully');
      }
      setEditDialogOpen(false);
      fetchDevotees();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to save devotee');
    }
  };
  
  const handleMerge = async () => {
    try {
      await api.post('/api/v1/devotees/merge', null, {
        params: {
          primary_id: mergeForm.primary_id,
          duplicate_ids: mergeForm.duplicate_ids,
        }
      });
      showSuccess('Devotees merged successfully');
      setMergeDialogOpen(false);
      fetchDuplicates();
      fetchDevotees();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to merge devotees');
    }
  };
  
  const handleLinkFamily = async () => {
    try {
      await api.put(`/api/v1/devotees/${selectedDevotee.id}/link-family`, null, {
        params: { family_head_id: familyForm.family_head_id }
      });
      showSuccess('Family member linked successfully');
      setFamilyDialogOpen(false);
      fetchDevotees();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to link family member');
    }
  };
  
  const handleUpdateTags = async () => {
    try {
      await api.put(`/api/v1/devotees/${selectedDevotee.id}/tags`, null, {
        params: { tags: devoteeForm.tags }
      });
      showSuccess('Tags updated successfully');
      setTagsDialogOpen(false);
      fetchDevotees();
    } catch (err) {
      showError(err.response?.data?.detail || 'Failed to update tags');
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Devotee CRM
        </Typography>
        <Button
          variant="contained"
          onClick={() => {
            setSelectedDevotee(null);
            setDevoteeForm({
              name: '', phone: '', email: '', address: '', city: '', state: '', pincode: '',
              country: 'India', date_of_birth: '', gothra: '', nakshatra: '',
              preferred_language: 'en', receive_sms: true, receive_email: true, tags: []
            });
            setEditDialogOpen(true);
          }}
        >
          Add Devotee
        </Button>
      </Box>

      <Paper sx={{ mt: 2 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="All Devotees" />
          <Tab label="Duplicates" />
          <Tab label="Upcoming Birthdays" />
          <Tab label="Analytics" />
        </Tabs>

        {tabValue === 0 && (
          <Box sx={{ p: 3 }}>
            {/* Search and Filters */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Search"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Name, phone, or email"
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <FormControl fullWidth>
                  <InputLabel>Filter by Tag</InputLabel>
                  <Select
                    value={selectedTag}
                    onChange={(e) => setSelectedTag(e.target.value)}
                    label="Filter by Tag"
                  >
                    <MenuItem value="">All</MenuItem>
                    {availableTags.map(tag => (
                      <MenuItem key={tag} value={tag}>{tag}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={3}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={showVipOnly}
                      onChange={(e) => setShowVipOnly(e.target.checked)}
                    />
                  }
                  label="VIP Only"
                />
              </Grid>
              <Grid item xs={12} sm={2}>
                <Button variant="outlined" onClick={fetchDuplicates} startIcon={<MergeIcon />}>
                  Find Duplicates
                </Button>
              </Grid>
            </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : devotees.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Phone</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Tags</TableCell>
                      <TableCell>Family</TableCell>
                      <TableCell align="right">Donations</TableCell>
                      <TableCell align="right">Total Donated</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {devotees.map((devotee) => (
                      <TableRow key={devotee.id || devotee.phone}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {devotee.is_vip && <StarIcon color="warning" fontSize="small" />}
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                              {devotee.name || devotee.full_name || 'N/A'}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <PhoneIcon fontSize="small" color="action" />
                            {devotee.phone || 'N/A'}
                          </Box>
                        </TableCell>
                        <TableCell>
                          {devotee.email ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <EmailIcon fontSize="small" color="action" />
                              {devotee.email}
                            </Box>
                          ) : (
                            'N/A'
                          )}
                        </TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={0.5} flexWrap="wrap">
                            {devotee.tags && devotee.tags.map(tag => (
                              <Chip key={tag} label={tag} size="small" />
                            ))}
                          </Stack>
                        </TableCell>
                        <TableCell>
                          {devotee.family_members_count > 0 ? (
                            <Chip
                              icon={<FamilyRestroomIcon />}
                              label={`${devotee.family_members_count} members`}
                              size="small"
                            />
                          ) : (
                            'None'
                          )}
                        </TableCell>
                        <TableCell align="right">{devotee.donation_count || 0}</TableCell>
                        <TableCell align="right">
                          {formatCurrency(devotee.total_donations || 0)}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton size="small" onClick={() => handleEdit(devotee)}>
                              <EditIcon fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedDevotee(devotee);
                                setFamilyDialogOpen(true);
                              }}
                            >
                              <FamilyRestroomIcon fontSize="small" />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => {
                                setSelectedDevotee(devotee);
                                setDevoteeForm({ ...devoteeForm, tags: devotee.tags || [] });
                                setTagsDialogOpen(true);
                              }}
                            >
                              <StarIcon fontSize="small" />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Box sx={{ textAlign: 'center', p: 4 }}>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  No devotees found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Devotees are automatically created when donations are recorded.
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {tabValue === 1 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Duplicate Devotees</Typography>
            {duplicates.length === 0 ? (
              <Alert severity="info">No duplicates found</Alert>
            ) : (
              duplicates.map((group, idx) => (
                <Paper key={idx} sx={{ p: 2, mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Duplicate Group {idx + 1} ({group.count} records)
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell>Phone</TableCell>
                          <TableCell>Email</TableCell>
                          <TableCell>City</TableCell>
                          <TableCell>Action</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {group.group.map((d) => (
                          <TableRow key={d.id}>
                            <TableCell>{d.name}</TableCell>
                            <TableCell>{d.phone}</TableCell>
                            <TableCell>{d.email || 'N/A'}</TableCell>
                            <TableCell>{d.city || 'N/A'}</TableCell>
                            <TableCell>
                              <Checkbox
                                checked={mergeForm.primary_id === d.id || mergeForm.duplicate_ids.includes(d.id)}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    if (!mergeForm.primary_id) {
                                      setMergeForm({ ...mergeForm, primary_id: d.id });
                                    } else {
                                      setMergeForm({
                                        ...mergeForm,
                                        duplicate_ids: [...mergeForm.duplicate_ids, d.id]
                                      });
                                    }
                                  }
                                }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                  <Button
                    variant="contained"
                    startIcon={<MergeIcon />}
                    onClick={handleMerge}
                    disabled={!mergeForm.primary_id || mergeForm.duplicate_ids.length === 0}
                    sx={{ mt: 2 }}
                  >
                    Merge Selected
                  </Button>
                </Paper>
              ))
            )}
          </Box>
        )}

        {tabValue === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Upcoming Birthdays (Next 30 Days)</Typography>
            {upcomingBirthdays.length === 0 ? (
              <Alert severity="info">No upcoming birthdays in the next 30 days</Alert>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Phone</TableCell>
                      <TableCell>Date of Birth</TableCell>
                      <TableCell>Email</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {upcomingBirthdays.map((devotee) => (
                      <TableRow key={devotee.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <CakeIcon color="primary" />
                            {devotee.name}
                          </Box>
                        </TableCell>
                        <TableCell>{devotee.phone}</TableCell>
                        <TableCell>
                          {devotee.date_of_birth ? new Date(devotee.date_of_birth).toLocaleDateString() : 'N/A'}
                        </TableCell>
                        <TableCell>{devotee.email || 'N/A'}</TableCell>
                        <TableCell>
                          <Button size="small" onClick={() => handleEdit(devotee)}>
                            Edit
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}

        {tabValue === 3 && analytics && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Devotee Analytics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Total Devotees</Typography>
                    <Typography variant="h4">{analytics.total_devotees}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Active Devotees</Typography>
                    <Typography variant="h4">{analytics.active_devotees}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>VIP Devotees</Typography>
                    <Typography variant="h4">{analytics.vip_count}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom>Family Groups</Typography>
                    <Typography variant="h4">{analytics.family_groups}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12}>
                <Paper sx={{ p: 2, mt: 2 }}>
                  <Typography variant="h6" gutterBottom>Top Donors</Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Name</TableCell>
                          <TableCell align="right">Total Donated</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {analytics.top_donors.map((donor) => (
                          <TableRow key={donor.id}>
                            <TableCell>{donor.name}</TableCell>
                            <TableCell align="right">{formatCurrency(donor.total_donated)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Edit Devotee Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{selectedDevotee ? 'Edit Devotee' : 'Add Devotee'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Name *"
                value={devoteeForm.name}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone *"
                value={devoteeForm.phone}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, phone: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={devoteeForm.email}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, email: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date of Birth"
                type="date"
                value={devoteeForm.date_of_birth}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, date_of_birth: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                value={devoteeForm.address}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, address: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="City"
                value={devoteeForm.city}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, city: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="State"
                value={devoteeForm.state}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, state: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Pincode"
                value={devoteeForm.pincode}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, pincode: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Gothra"
                value={devoteeForm.gothra}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, gothra: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nakshatra"
                value={devoteeForm.nakshatra}
                onChange={(e) => setDevoteeForm({ ...devoteeForm, nakshatra: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Preferred Language</InputLabel>
                <Select
                  value={devoteeForm.preferred_language}
                  onChange={(e) => setDevoteeForm({ ...devoteeForm, preferred_language: e.target.value })}
                  label="Preferred Language"
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="hi">Hindi</MenuItem>
                  <MenuItem value="kn">Kannada</MenuItem>
                  <MenuItem value="ta">Tamil</MenuItem>
                  <MenuItem value="te">Telugu</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={devoteeForm.receive_sms}
                    onChange={(e) => setDevoteeForm({ ...devoteeForm, receive_sms: e.target.checked })}
                  />
                }
                label="Receive SMS"
              />
              <FormControlLabel
                control={
                  <Checkbox
                    checked={devoteeForm.receive_email}
                    onChange={(e) => setDevoteeForm({ ...devoteeForm, receive_email: e.target.checked })}
                  />
                }
                label="Receive Email"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveDevotee}>
            {selectedDevotee ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Link Family Dialog */}
      <Dialog open={familyDialogOpen} onClose={() => setFamilyDialogOpen(false)}>
        <DialogTitle>Link Family Member</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Family Head</InputLabel>
            <Select
              value={familyForm.family_head_id}
              onChange={(e) => setFamilyForm({ ...familyForm, family_head_id: e.target.value })}
              label="Family Head"
            >
              {devotees.map(d => (
                <MenuItem key={d.id} value={d.id}>{d.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Linking {selectedDevotee?.name} to selected family head
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFamilyDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleLinkFamily} disabled={!familyForm.family_head_id}>
            Link
          </Button>
        </DialogActions>
      </Dialog>

      {/* Tags Dialog */}
      <Dialog open={tagsDialogOpen} onClose={() => setTagsDialogOpen(false)}>
        <DialogTitle>Update Tags</DialogTitle>
        <DialogContent>
          <Autocomplete
            multiple
            options={availableTags}
            value={devoteeForm.tags}
            onChange={(e, newValue) => setDevoteeForm({ ...devoteeForm, tags: newValue })}
            renderInput={(params) => <TextField {...params} label="Tags" sx={{ mt: 2 }} />}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  {...getTagProps({ index })}
                  key={option}
                />
              ))
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTagsDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdateTags}>
            Update Tags
          </Button>
        </DialogActions>
      </Dialog>
    </Layout>
  );
}

export default Devotees;
