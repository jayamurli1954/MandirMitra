import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Paper,
  Stack,
  CircularProgress,
  Tab,
  Tabs,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import api from '../services/api';

function Sevas() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const [sevas, setSevas] = useState([]);
  const [filteredSevas, setFilteredSevas] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Booking dialog state
  const [bookingDialogOpen, setBookingDialogOpen] = useState(false);
  const [selectedSeva, setSelectedSeva] = useState(null);
  const [, setDevotees] = useState([]);
  const [bookingForm, setBookingForm] = useState({
    devotee_id: '',
    booking_date: new Date().toISOString().split('T')[0],
    booking_time: '',
    amount_paid: '',
    payment_method: 'cash',
    devotee_names: '',
    gotra: '',
    nakshatra: '',
    rashi: '',
    special_request: ''
  });
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [bookingError, setBookingError] = useState(null);

  // Mobile-first workflow state
  const [mobileNumber, setMobileNumber] = useState('');
  const [searchingDevotee, setSearchingDevotee] = useState(false);
  const [foundDevotee, setFoundDevotee] = useState(null);
  const [showNewDevoteeForm, setShowNewDevoteeForm] = useState(false);
  const [newDevoteeData, setNewDevoteeData] = useState({
    name: '',
    address: '',
    pincode: '',
    city: '',
    state: '',
    country: 'India'
  });
  const [lookingUpPincode, setLookingUpPincode] = useState(false);

  // Dropdown options state
  const [dropdownOptions, setDropdownOptions] = useState({
    gothras: [],
    nakshatras: [],
    rashis: []
  });

  useEffect(() => {
    fetchSevas();
    fetchDevotees();
    fetchDropdownOptions();
  }, []);

  useEffect(() => {
    filterSevas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sevas, selectedCategory]);

  const fetchSevas = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/v1/sevas/');
      
      if (response.data && Array.isArray(response.data)) {
        setSevas(response.data);

        // Extract unique categories
        const uniqueCategories = [...new Set(response.data.map(s => s.category))];
        setCategories(uniqueCategories);
      } else {
        setError('Invalid response format from server');
      }

      setLoading(false);
    } catch (err) {
      console.error('Error fetching sevas:', err);
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load sevas. Please check if backend is running.';
      setError(errorMsg);
      setLoading(false);
    }
  };

  const fetchDevotees = async () => {
    try {
      const response = await api.get('/api/v1/devotees/');
      setDevotees(response.data);
    } catch (err) {
      console.error('Failed to load devotees');
    }
  };

  const fetchDropdownOptions = async () => {
    try {
      const response = await api.get('/api/v1/sevas/dropdown-options');
      console.log('Dropdown options response:', response.data);
      if (response.data) {
        setDropdownOptions({
          gothras: response.data.gothras || response.data.GOTHRAS || [],
          nakshatras: response.data.nakshatras || response.data.NAKSHATRAS || [],
          rashis: response.data.rashis || response.data.RASHIS || []
        });
      }
    } catch (err) {
      console.error('Failed to load dropdown options:', err);
      // Fallback to hardcoded values if API fails
      setDropdownOptions({
        gothras: [
          "Agastya", "Angirasa", "Atri", "Bharadwaja", "Bhargava", "Bhrigu",
          "Dhananjaya", "Garga", "Gautama", "Harita", "Jamadagni", "Kashyapa",
          "Katyayana", "Kaundinya", "Kausika", "Kaushika", "Kratu", "Kutsa",
          "Lomasha", "Mandavya", "Marichi", "Moudgalya", "Naidhruva", "Parashara",
          "Pulaha", "Pulastya", "Sandilya", "Shandilya", "Sankrithi", "Srivatsa",
          "Upamanyu", "Valmiki", "Vashishta", "Vatsa", "Vishwamitra", "Viswamitra",
          "Vrigu", "Yaska", "Kanva", "Mudgala", "Raibhya", "Uddālaka", "Agni",
          "Aliman", "Kapi", "Krivi", "Saunaka", "Vadula", "Vasistha"
        ],
        nakshatras: [
          "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
          "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
          "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
          "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
          "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ],
        rashis: [
          "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
          "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)",
          "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
        ]
      });
    }
  };

  const filterSevas = () => {
    if (selectedCategory === 'all') {
      setFilteredSevas(sevas);
    } else {
      setFilteredSevas(sevas.filter(s => s.category === selectedCategory));
    }
  };

  const handleBookNow = (seva) => {
    setSelectedSeva(seva);
    setBookingForm({
      ...bookingForm,
      amount_paid: seva.amount
    });
    setBookingDialogOpen(true);
  };

  const handleSearchByMobile = async () => {
    if (!mobileNumber || mobileNumber.length < 10) {
      setBookingError('Please enter a valid 10-digit mobile number');
      return;
    }

    setSearchingDevotee(true);
    setBookingError(null);

    try {
      const response = await api.get(`/api/v1/devotees/search/by-mobile/${mobileNumber}`);

      if (response.data) {
        // Devotee found
        setFoundDevotee(response.data);
        setShowNewDevoteeForm(false);
        setBookingForm({ ...bookingForm, devotee_id: response.data.id });
      } else {
        // Devotee not found - show create form
        setFoundDevotee(null);
        setShowNewDevoteeForm(true);
        setNewDevoteeData({ name: '', address: '', pincode: '', city: '', state: '', country: 'India' });
      }
    } catch (err) {
      // Devotee not found - show create form
      setFoundDevotee(null);
      setShowNewDevoteeForm(true);
      setNewDevoteeData({ name: '', address: '', pincode: '', city: '', state: '', country: 'India' });
    } finally {
      setSearchingDevotee(false);
    }
  };

  const lookupPincode = async (pincode) => {
    if (!pincode || pincode.length !== 6) return null;
    
    setLookingUpPincode(true);
    try {
      const response = await fetch(`https://api.postalpincode.in/pincode/${pincode}`);
      const data = await response.json();
      
      if (data && data[0] && data[0].Status === 'Success' && data[0].PostOffice && data[0].PostOffice.length > 0) {
        const postOffice = data[0].PostOffice[0];
        return {
          city: postOffice.District || postOffice.Name || '',
          state: postOffice.State || '',
          country: 'India'
        };
      }
    } catch (err) {
      console.error('Error looking up pincode:', err);
    } finally {
      setLookingUpPincode(false);
    }
    return null;
  };

  const handlePincodeChange = async (pincode) => {
    setNewDevoteeData({ ...newDevoteeData, pincode });
    
    if (pincode && pincode.length === 6) {
      const locationData = await lookupPincode(pincode);
      if (locationData) {
        setNewDevoteeData({
          ...newDevoteeData,
          pincode,
          city: locationData.city || '',
          state: locationData.state || '',
          country: locationData.country || 'India'
        });
      }
    }
  };

  const handleCreateDevotee = async () => {
    if (!newDevoteeData.name) {
      setBookingError('Please enter devotee name');
      return;
    }

    try {
      const devoteeData = {
        name: newDevoteeData.name,
        phone: mobileNumber,
        address: newDevoteeData.address,
        city: newDevoteeData.city,
        state: newDevoteeData.state,
        pincode: newDevoteeData.pincode,
        country: newDevoteeData.country || 'India'
      };

      const response = await api.post('/api/v1/devotees/', devoteeData);
      setFoundDevotee(response.data);
      setShowNewDevoteeForm(false);
      setBookingForm({ ...bookingForm, devotee_id: response.data.id });

      // Refresh devotees list
      fetchDevotees();
    } catch (err) {
      setBookingError(err.response?.data?.detail || 'Failed to create devotee');
    }
  };

  const handleBookingSubmit = async () => {
    try {
      setBookingError(null);
      const bookingData = {
        ...bookingForm,
        seva_id: selectedSeva.id
      };

      console.log('Submitting booking:', bookingData);
      const response = await api.post('/api/v1/sevas/bookings/', bookingData);
      console.log('Booking created successfully:', response.data);
      
      setBookingSuccess(true);

      // Refresh sevas list to show updated availability
      await fetchSevas();

      // Reset and close after 2 seconds
      setTimeout(() => {
        setBookingDialogOpen(false);
        setBookingSuccess(false);
        setMobileNumber('');
        setFoundDevotee(null);
        setShowNewDevoteeForm(false);
        setNewDevoteeData({
          name: '',
          address: '',
          pincode: '',
          city: '',
          state: '',
          country: 'India'
        });
        setBookingForm({
          devotee_id: '',
          booking_date: new Date().toISOString().split('T')[0],
          booking_time: '',
          amount_paid: '',
          payment_method: 'cash',
          devotee_names: '',
          gotra: '',
          nakshatra: '',
          rashi: '',
          special_request: ''
        });
      }, 2000);
    } catch (err) {
      console.error('Booking error:', err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to book seva';
      setBookingError(errorMessage);
      console.error('Error details:', err.response?.data);
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      abhisheka: '#2E7D32',
      alankara: '#1565C0',
      pooja: '#7B1FA2',
      archana: '#F57C00',
      vahana_seva: '#00796B',
      special: '#C62828',
      festival: '#FF6B35'
    };
    return colors[category] || '#666';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      abhisheka: '💧',
      alankara: '🌸',
      pooja: '🙏',
      archana: '📿',
      vahana_seva: '🚩',
      special: '⭐',
      festival: '🎉'
    };
    return icons[category] || '🕉️';
  };

  const formatCategory = (category) => {
    return category.split('_').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
        {/* Header */}
        <Paper sx={{ p: 2, mb: 3, background: 'linear-gradient(135deg, #FF9933 0%, #FF6B35 100%)' }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: '#fff', mb: 0.5 }}>
                🕉️ Temple Sevas & Services
              </Typography>
              <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                Book divine sevas and poojas for blessings and spiritual upliftment
              </Typography>
            </Box>
            {user.role === 'admin' && (
              <Button
                variant="contained"
                startIcon={<SettingsIcon />}
                onClick={() => navigate('/sevas/manage')}
                sx={{
                  bgcolor: '#fff',
                  color: '#FF6B35',
                  '&:hover': { bgcolor: '#f5f5f5' }
                }}
              >
                Manage Sevas
              </Button>
            )}
          </Box>
        </Paper>

        {/* Category Filter */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Tabs
            value={selectedCategory}
            onChange={(e, newValue) => setSelectedCategory(newValue)}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="All Sevas" value="all" />
            {categories.map(cat => (
              <Tab
                key={cat}
                label={`${getCategoryIcon(cat)} ${formatCategory(cat)}`}
                value={cat}
              />
            ))}
          </Tabs>
        </Paper>

        {/* Sevas Grid */}
        <Grid container spacing={2}>
          {filteredSevas.map((seva) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={seva.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderLeft: `4px solid ${getCategoryColor(seva.category)}`,
                  '&:hover': {
                    boxShadow: 6,
                    transform: 'translateY(-2px)',
                    transition: 'all 0.3s'
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Category Badge */}
                  <Chip
                    label={`${getCategoryIcon(seva.category)} ${formatCategory(seva.category)}`}
                    size="small"
                    sx={{
                      mb: 1,
                      bgcolor: getCategoryColor(seva.category),
                      color: '#fff',
                      fontWeight: 600
                    }}
                  />

                  {/* Seva Name */}
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5, color: getCategoryColor(seva.category) }}>
                    {seva.name_english}
                  </Typography>
                  {seva.name_kannada && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {seva.name_kannada}
                    </Typography>
                  )}

                  {/* Description */}
                  {seva.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {seva.description}
                    </Typography>
                  )}

                  {/* Time Slot */}
                  {seva.time_slot && (
                    <Chip
                      label={`⏰ ${seva.time_slot}`}
                      size="small"
                      variant="outlined"
                      sx={{ mb: 1, mr: 1 }}
                    />
                  )}

                  {/* Availability */}
                  {seva.availability !== 'daily' && (
                    <Chip
                      label={
                        seva.specific_day !== null
                          ? `📅 ${['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][seva.specific_day]} Only`
                          : seva.except_day !== null
                          ? `📅 Except ${['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][seva.except_day]}`
                          : formatCategory(seva.availability)
                      }
                      size="small"
                      variant="outlined"
                      sx={{ mb: 1 }}
                    />
                  )}

                  {/* Availability Status */}
                  {seva.is_available_today ? (
                    <Chip
                      label="✅ Available Today"
                      size="small"
                      sx={{ bgcolor: '#E8F5E9', color: '#2E7D32', mb: 1, display: 'block', width: 'fit-content' }}
                    />
                  ) : (
                    <Chip
                      label="❌ Not Available Today"
                      size="small"
                      sx={{ bgcolor: '#FFEBEE', color: '#C62828', mb: 1, display: 'block', width: 'fit-content' }}
                    />
                  )}

                  {/* Price */}
                  <Box sx={{ mt: 'auto', pt: 2 }}>
                    {seva.min_amount && seva.max_amount ? (
                      <Typography variant="h6" sx={{ fontWeight: 700, color: getCategoryColor(seva.category) }}>
                        ₹{seva.min_amount} - ₹{seva.max_amount}
                      </Typography>
                    ) : (
                      <Typography variant="h6" sx={{ fontWeight: 700, color: getCategoryColor(seva.category) }}>
                        ₹{seva.amount}
                      </Typography>
                    )}
                  </Box>
                </CardContent>

                {/* Book Button */}
                <Box sx={{ p: 2, pt: 0 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={() => handleBookNow(seva)}
                    disabled={!seva.is_active}
                    sx={{
                      bgcolor: getCategoryColor(seva.category),
                      '&:hover': {
                        bgcolor: getCategoryColor(seva.category),
                        filter: 'brightness(0.9)'
                      }
                    }}
                  >
                    Book Now
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Booking Dialog */}
        <Dialog
          open={bookingDialogOpen}
          onClose={() => setBookingDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Book {selectedSeva?.name_english}
            </Typography>
            {selectedSeva?.name_kannada && (
              <Typography variant="body2" color="text.secondary">
                {selectedSeva.name_kannada}
              </Typography>
            )}
          </DialogTitle>
          <DialogContent dividers>
            {bookingSuccess && (
              <Alert severity="success" sx={{ mb: 2 }}>
                Seva booked successfully! Receipt will be generated.
              </Alert>
            )}
            {bookingError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {bookingError}
              </Alert>
            )}

            <Stack spacing={2}>
              {/* Mobile Number Input - STEP 1 */}
              {!foundDevotee && !showNewDevoteeForm && (
                <Box>
                  <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                    Step 1: Enter Devotee Mobile Number *
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      label="Mobile Number"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      placeholder="Enter 10-digit mobile"
                      fullWidth
                      inputProps={{ maxLength: 10 }}
                    />
                    <Button
                      variant="contained"
                      onClick={handleSearchByMobile}
                      disabled={searchingDevotee || mobileNumber.length < 10}
                      sx={{ minWidth: 100 }}
                    >
                      {searchingDevotee ? <CircularProgress size={24} /> : 'Search'}
                    </Button>
                  </Box>
                </Box>
              )}

              {/* Found Devotee - STEP 2a */}
              {foundDevotee && (
                <Box>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    ✅ Devotee Found!
                  </Alert>
                  <Paper sx={{ p: 2, bgcolor: '#E8F5E9' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Devotee Details:
                    </Typography>
                    <Typography variant="body2"><strong>Name:</strong> {foundDevotee.name}</Typography>
                    <Typography variant="body2"><strong>Phone:</strong> {foundDevotee.phone}</Typography>
                    {foundDevotee.address && (
                      <Typography variant="body2"><strong>Address:</strong> {foundDevotee.address}</Typography>
                    )}
                    <Button
                      size="small"
                      onClick={() => {
                        setFoundDevotee(null);
                        setMobileNumber('');
                        setBookingForm({ ...bookingForm, devotee_id: '' });
                      }}
                      sx={{ mt: 1 }}
                    >
                      Change Devotee
                    </Button>
                  </Paper>
                </Box>
              )}

              {/* New Devotee Form - STEP 2b */}
              {showNewDevoteeForm && (
                <Box>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    ℹ️ Devotee not found. Please enter details to create new devotee.
                  </Alert>
                  <Paper sx={{ p: 2, bgcolor: '#FFF3E0' }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                      New Devotee Details:
                    </Typography>
                    <Stack spacing={2}>
                      <TextField
                        label="Name *"
                        value={newDevoteeData.name}
                        onChange={(e) => setNewDevoteeData({ ...newDevoteeData, name: e.target.value })}
                        fullWidth
                        size="small"
                      />
                      <TextField
                        label="Address"
                        value={newDevoteeData.address}
                        onChange={(e) => setNewDevoteeData({ ...newDevoteeData, address: e.target.value })}
                        fullWidth
                        size="small"
                      />
                      {/* PIN Code - Early field for auto-fill */}
                      <TextField
                        label="PIN Code"
                        value={newDevoteeData.pincode}
                        onChange={(e) => handlePincodeChange(e.target.value)}
                        size="small"
                        inputProps={{ maxLength: 6 }}
                        fullWidth
                        helperText={lookingUpPincode ? 'Looking up...' : (newDevoteeData.pincode && newDevoteeData.pincode.length === 6 ? 'Auto-fills city/state below' : 'Enter 6-digit PIN code')}
                        InputProps={{
                          endAdornment: lookingUpPincode ? <CircularProgress size={16} /> : null
                        }}
                      />
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <TextField
                          label="City"
                          value={newDevoteeData.city}
                          onChange={(e) => setNewDevoteeData({ ...newDevoteeData, city: e.target.value })}
                          size="small"
                          sx={{ flex: 1 }}
                          helperText={newDevoteeData.city ? '✓ Auto-filled' : ''}
                        />
                        <TextField
                          label="State"
                          value={newDevoteeData.state}
                          onChange={(e) => setNewDevoteeData({ ...newDevoteeData, state: e.target.value })}
                          size="small"
                          sx={{ flex: 1 }}
                          helperText={newDevoteeData.state ? '✓ Auto-filled' : ''}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="contained"
                          onClick={handleCreateDevotee}
                          fullWidth
                          disabled={!newDevoteeData.name}
                        >
                          Create & Continue
                        </Button>
                        <Button
                          variant="outlined"
                          onClick={() => {
                            setShowNewDevoteeForm(false);
                            setMobileNumber('');
                          }}
                        >
                          Cancel
                        </Button>
                      </Box>
                    </Stack>
                  </Paper>
                </Box>
              )}

              {/* Booking Details - Only show after devotee is selected */}
              {foundDevotee && (
                <>
                  <Typography variant="subtitle2" sx={{ mt: 2, fontWeight: 600, color: '#FF9933' }}>
                    Step 2: Seva Booking Details
                  </Typography>

              {/* Booking Date */}
              <TextField
                label="Booking Date *"
                type="date"
                value={bookingForm.booking_date}
                onChange={(e) => setBookingForm({...bookingForm, booking_date: e.target.value})}
                InputLabelProps={{ shrink: true }}
                inputProps={{ min: new Date().toISOString().split('T')[0] }}
                fullWidth
              />

              {/* Booking Time (if applicable) */}
              {selectedSeva?.time_slot && (
                <TextField
                  label="Preferred Time"
                  value={bookingForm.booking_time}
                  onChange={(e) => setBookingForm({...bookingForm, booking_time: e.target.value})}
                  helperText={`Recommended: ${selectedSeva.time_slot}`}
                  fullWidth
                />
              )}

              {/* Amount */}
              <TextField
                label="Amount *"
                type="number"
                value={bookingForm.amount_paid}
                onChange={(e) => setBookingForm({...bookingForm, amount_paid: parseFloat(e.target.value)})}
                InputProps={{
                  startAdornment: '₹'
                }}
                fullWidth
              />

              {/* Payment Method */}
              <FormControl fullWidth>
                <InputLabel>Payment Method *</InputLabel>
                <Select
                  value={bookingForm.payment_method}
                  onChange={(e) => setBookingForm({...bookingForm, payment_method: e.target.value})}
                  label="Payment Method *"
                >
                  <MenuItem value="cash">Cash</MenuItem>
                  <MenuItem value="upi">UPI</MenuItem>
                  <MenuItem value="card">Card</MenuItem>
                  <MenuItem value="online">Online Transfer</MenuItem>
                </Select>
              </FormControl>

              {/* Additional Names */}
              <TextField
                label="Additional Devotee Names"
                value={bookingForm.devotee_names}
                onChange={(e) => setBookingForm({...bookingForm, devotee_names: e.target.value})}
                placeholder="Names for whom seva is performed (comma separated)"
                multiline
                rows={2}
                fullWidth
              />

              {/* Gotra */}
              <FormControl fullWidth>
                <InputLabel>Gotra</InputLabel>
                <Select
                  value={bookingForm.gotra}
                  onChange={(e) => setBookingForm({...bookingForm, gotra: e.target.value})}
                  label="Gotra"
                >
                  <MenuItem value="">
                    <em>Select Gotra</em>
                  </MenuItem>
                  {dropdownOptions.gothras && dropdownOptions.gothras.length > 0 ? (
                    dropdownOptions.gothras.map((gotra) => (
                      <MenuItem key={gotra} value={gotra}>
                        {gotra}
                      </MenuItem>
                    ))
                  ) : (
                    <MenuItem disabled>Loading...</MenuItem>
                  )}
                </Select>
              </FormControl>

              {/* Nakshatra */}
              <FormControl fullWidth>
                <InputLabel>Nakshatra</InputLabel>
                <Select
                  value={bookingForm.nakshatra}
                  onChange={(e) => setBookingForm({...bookingForm, nakshatra: e.target.value})}
                  label="Nakshatra"
                >
                  <MenuItem value="">
                    <em>Select Nakshatra</em>
                  </MenuItem>
                  {dropdownOptions.nakshatras && dropdownOptions.nakshatras.length > 0 ? (
                    dropdownOptions.nakshatras.map((nakshatra) => (
                      <MenuItem key={nakshatra} value={nakshatra}>
                        {nakshatra}
                      </MenuItem>
                    ))
                  ) : (
                    <MenuItem disabled>Loading...</MenuItem>
                  )}
                </Select>
              </FormControl>

              {/* Rashi */}
              <FormControl fullWidth>
                <InputLabel>Rashi</InputLabel>
                <Select
                  value={bookingForm.rashi}
                  onChange={(e) => setBookingForm({...bookingForm, rashi: e.target.value})}
                  label="Rashi"
                >
                  <MenuItem value="">
                    <em>Select Rashi</em>
                  </MenuItem>
                  {dropdownOptions.rashis && dropdownOptions.rashis.length > 0 ? (
                    dropdownOptions.rashis.map((rashi) => (
                      <MenuItem key={rashi} value={rashi}>
                        {rashi}
                      </MenuItem>
                    ))
                  ) : (
                    <MenuItem disabled>Loading...</MenuItem>
                  )}
                </Select>
              </FormControl>

              {/* Special Request */}
              <TextField
                label="Special Request / Instructions"
                value={bookingForm.special_request}
                onChange={(e) => setBookingForm({...bookingForm, special_request: e.target.value})}
                multiline
                rows={3}
                fullWidth
              />
                </>
              )}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setBookingDialogOpen(false)}>Cancel</Button>
            <Button
              onClick={handleBookingSubmit}
              variant="contained"
              disabled={!bookingForm.devotee_id || !bookingForm.amount_paid || bookingSuccess}
            >
              Confirm Booking
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
  );
}

export default Sevas;
