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
    payment_method: 'Cash',
    // UPI Payment Details
    sender_upi_id: '',
    upi_reference_number: '',
    // Cheque Payment Details
    cheque_number: '',
    cheque_date: '',
    cheque_bank_name: '',
    cheque_branch: '',
    // Online Transfer Details
    utr_number: '',
    payer_name: '',
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
  const [countryCode, setCountryCode] = useState('+91'); // Default to India
  const [searchingDevotee, setSearchingDevotee] = useState(false);
  const [foundDevotee, setFoundDevotee] = useState(null);
  const [showNewDevoteeForm, setShowNewDevoteeForm] = useState(false);
  const [newDevoteeData, setNewDevoteeData] = useState({
    first_name: '',
    last_name: '',
    name_prefix: '',
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
    // For India (+91), require 10 digits; for others, require at least 7 digits
    const isValidLength = (countryCode === '+91' && mobileNumber.length === 10) || 
                         (countryCode !== '+91' && mobileNumber.length >= 7);
    
    if (!mobileNumber || !isValidLength) {
      setBookingError(`Please enter a valid mobile number${countryCode === '+91' ? ' (10 digits)' : ''}`);
      return;
    }

    setSearchingDevotee(true);
    setBookingError(null);

    try {
      // Search with country code
      const searchPhone = `${countryCode}${mobileNumber}`;
      console.log('Searching devotee with phone:', searchPhone);
      const response = await api.get(`/api/v1/devotees/search/by-mobile/${encodeURIComponent(searchPhone)}`);

      console.log('Search response:', response.data);
      
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        // Use first match (prioritized by country code match)
        const devotee = response.data[0];
        console.log('Found devotee:', devotee);
        setFoundDevotee(devotee);
        setShowNewDevoteeForm(false);
        setBookingForm({ ...bookingForm, devotee_id: devotee.id });
        setBookingError(null); // Clear any previous errors
      } else {
        // Devotee not found - show create form
        console.log('No devotee found, showing create form');
        setFoundDevotee(null);
        setShowNewDevoteeForm(true);
        setBookingError(null); // Clear error - this is expected when devotee doesn't exist
        setNewDevoteeData({ 
          first_name: '', 
          last_name: '',
          name_prefix: '',
          address: '', 
          pincode: '', 
          city: '', 
          state: '', 
          country: 'India' 
        });
      }
    } catch (err) {
      console.error('Error searching devotee:', err);
      // If it's a 404 or empty result, show create form
      if (err.response?.status === 404 || err.response?.status === 200) {
        setFoundDevotee(null);
        setShowNewDevoteeForm(true);
        setBookingError(null); // Clear error - this is expected
        setNewDevoteeData({ 
          first_name: '', 
          last_name: '',
          name_prefix: '',
          address: '', 
          pincode: '', 
          city: '', 
          state: '', 
          country: 'India' 
        });
      } else {
        // Real error - show it
        let errorMsg = 'Failed to search devotee';
        if (err.response?.data?.detail) {
          const detail = err.response.data.detail;
          if (Array.isArray(detail)) {
            errorMsg = detail.map(err => err.msg || 'Invalid value').join('; ');
          } else if (typeof detail === 'string') {
            errorMsg = detail;
          } else {
            errorMsg = JSON.stringify(detail);
          }
        } else if (err.response?.data?.message) {
          errorMsg = err.response.data.message;
        } else if (err.message) {
          errorMsg = err.message;
        }
        setBookingError(errorMsg);
        setFoundDevotee(null);
        setShowNewDevoteeForm(false);
      }
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
    if (!newDevoteeData.first_name) {
      setBookingError('Please enter devotee first name');
      return;
    }

    if (!mobileNumber || (countryCode === '+91' && mobileNumber.length !== 10)) {
      setBookingError('Please enter a valid mobile number');
      return;
    }

    setSearchingDevotee(true);
    setBookingError(null);

    try {
      // Send phone with country code - backend will normalize it
      const devoteeData = {
        first_name: newDevoteeData.first_name,
        last_name: newDevoteeData.last_name || undefined,
        name_prefix: newDevoteeData.name_prefix || undefined,
        country_code: countryCode,
        phone: `${countryCode}${mobileNumber}`,  // Backend will normalize this
        address: newDevoteeData.address || undefined,
        city: newDevoteeData.city || undefined,
        state: newDevoteeData.state || undefined,
        pincode: newDevoteeData.pincode || undefined,
        country: newDevoteeData.country || 'India'
      };

      const response = await api.post('/api/v1/devotees/', devoteeData);
      
      if (response.data) {
        setFoundDevotee(response.data);
        setShowNewDevoteeForm(false);
        setBookingForm({ ...bookingForm, devotee_id: response.data.id });
        setBookingError(null);
        
        // Refresh devotees list
        fetchDevotees();
      }
    } catch (err) {
      console.error('Error creating devotee:', err);
      
      // Handle FastAPI validation errors (422) - detail is an array of error objects
      let errorMsg = 'Failed to create devotee';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // FastAPI validation error - extract messages from array
          errorMsg = detail.map(err => {
            const field = err.loc ? err.loc.join('.') : 'field';
            return `${field}: ${err.msg || 'Invalid value'}`;
          }).join('; ');
        } else if (typeof detail === 'string') {
          // Simple string error
          errorMsg = detail;
        } else {
          // Object error - convert to string
          errorMsg = JSON.stringify(detail);
        }
      } else if (err.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      // Handle specific error cases
      if (errorMsg.includes('Phone number already exists')) {
        // Check if error contains devotee ID - if so, try to fetch and use that devotee
        const devoteeIdMatch = errorMsg.match(/Devotee ID: (\d+)/);
        if (devoteeIdMatch) {
          const existingDevoteeId = parseInt(devoteeIdMatch[1]);
          // Try to fetch the existing devotee
          try {
            const devoteeResponse = await api.get(`/api/v1/devotees/${existingDevoteeId}`);
            if (devoteeResponse.data) {
              // Found the existing devotee - use it
              setFoundDevotee(devoteeResponse.data);
              setShowNewDevoteeForm(false);
              setBookingForm({ ...bookingForm, devotee_id: devoteeResponse.data.id });
              setBookingError(null);
              return; // Success - don't show error
            }
          } catch (fetchErr) {
            console.error('Error fetching existing devotee:', fetchErr);
            // Fall through to show error message
          }
        }
        
        // Phone exists but couldn't fetch devotee - suggest searching instead
        setBookingError(
          `${errorMsg}. Please use the Search button to find the existing devotee instead of creating a new one.`
        );
        // Clear the new devotee form and suggest searching
        setShowNewDevoteeForm(false);
        setFoundDevotee(null);
      } else {
        setBookingError(errorMsg);
      }
    } finally {
      setSearchingDevotee(false);
    }
  };

  const handleBookingSubmit = async () => {
    try {
      setBookingError(null);
      
      // Validate required fields
      if (!selectedSeva || !selectedSeva.id) {
        setBookingError('Please select a seva');
        return;
      }
      
      // If devotee not found yet, create it first
      let devoteeId = bookingForm.devotee_id ? parseInt(bookingForm.devotee_id) : null;
      
      if (!devoteeId || isNaN(devoteeId)) {
        // Check if we have new devotee data to create
        if (!foundDevotee && showNewDevoteeForm && newDevoteeData.first_name) {
          // Create devotee first
          if (!mobileNumber || (countryCode === '+91' && mobileNumber.length !== 10)) {
            setBookingError('Please enter a valid mobile number');
            return;
          }
          
          try {
            const devoteeData = {
              first_name: newDevoteeData.first_name,
              last_name: newDevoteeData.last_name || undefined,
              name_prefix: newDevoteeData.name_prefix || undefined,
              country_code: countryCode,
              phone: `${countryCode}${mobileNumber}`,
              address: newDevoteeData.address || undefined,
              city: newDevoteeData.city || undefined,
              state: newDevoteeData.state || undefined,
              pincode: newDevoteeData.pincode || undefined,
              country: newDevoteeData.country || 'India'
            };
            
            const devoteeResponse = await api.post('/api/v1/devotees/', devoteeData);
            if (devoteeResponse.data) {
              devoteeId = devoteeResponse.data.id;
              setFoundDevotee(devoteeResponse.data);
              setBookingForm({ ...bookingForm, devotee_id: devoteeId });
            }
          } catch (err) {
            let errorMsg = 'Failed to create devotee';
            if (err.response?.data?.detail) {
              const detail = err.response.data.detail;
              if (Array.isArray(detail)) {
                errorMsg = detail.map(e => e.msg || 'Invalid value').join('; ');
              } else if (typeof detail === 'string') {
                errorMsg = detail;
              }
            }
            setBookingError(errorMsg);
            return;
          }
        } else {
          setBookingError('Please search for devotee by mobile number first');
          return;
        }
      }
      
      if (!bookingForm.booking_date) {
        setBookingError('Please select a booking date');
        return;
      }
      
      const amountPaid = bookingForm.amount_paid ? parseFloat(bookingForm.amount_paid) : null;
      if (!amountPaid || isNaN(amountPaid) || amountPaid <= 0) {
        setBookingError('Please enter a valid amount (greater than 0)');
        return;
      }
      
      // Prepare booking data - only include defined fields, convert empty strings to undefined
      const bookingData = {
        seva_id: selectedSeva.id,
        devotee_id: devoteeId,
        booking_date: bookingForm.booking_date,
        amount_paid: amountPaid,
        payment_method: bookingForm.payment_method || 'Cash'
      };
      
      // Add optional fields only if they have values
      if (bookingForm.booking_time && bookingForm.booking_time.trim()) {
        bookingData.booking_time = bookingForm.booking_time.trim();
      }
      
      // Payment-specific fields - only include if they have values
      if (bookingForm.sender_upi_id && bookingForm.sender_upi_id.trim()) {
        bookingData.sender_upi_id = bookingForm.sender_upi_id.trim();
      }
      if (bookingForm.upi_reference_number && bookingForm.upi_reference_number.trim()) {
        bookingData.upi_reference_number = bookingForm.upi_reference_number.trim();
      }
      if (bookingForm.cheque_number && bookingForm.cheque_number.trim()) {
        bookingData.cheque_number = bookingForm.cheque_number.trim();
      }
      if (bookingForm.cheque_date && bookingForm.cheque_date.trim()) {
        bookingData.cheque_date = bookingForm.cheque_date.trim();
      }
      if (bookingForm.cheque_bank_name && bookingForm.cheque_bank_name.trim()) {
        bookingData.cheque_bank_name = bookingForm.cheque_bank_name.trim();
      }
      if (bookingForm.cheque_branch && bookingForm.cheque_branch.trim()) {
        bookingData.cheque_branch = bookingForm.cheque_branch.trim();
      }
      if (bookingForm.utr_number && bookingForm.utr_number.trim()) {
        bookingData.utr_number = bookingForm.utr_number.trim();
      }
      if (bookingForm.payer_name && bookingForm.payer_name.trim()) {
        bookingData.payer_name = bookingForm.payer_name.trim();
      }
      
      // Optional devotee details
      if (bookingForm.devotee_names && bookingForm.devotee_names.trim()) {
        bookingData.devotee_names = bookingForm.devotee_names.trim();
      }
      if (bookingForm.gotra && bookingForm.gotra.trim()) {
        bookingData.gotra = bookingForm.gotra.trim();
      }
      if (bookingForm.nakshatra && bookingForm.nakshatra.trim()) {
        bookingData.nakshatra = bookingForm.nakshatra.trim();
      }
      if (bookingForm.rashi && bookingForm.rashi.trim()) {
        bookingData.rashi = bookingForm.rashi.trim();
      }
      if (bookingForm.special_request && bookingForm.special_request.trim()) {
        bookingData.special_request = bookingForm.special_request.trim();
      }

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
        setCountryCode('+91');
        setFoundDevotee(null);
        setShowNewDevoteeForm(false);
        setNewDevoteeData({
          first_name: '',
          last_name: '',
          name_prefix: '',
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
          payment_method: 'Cash',
          sender_upi_id: '',
          upi_reference_number: '',
          cheque_number: '',
          cheque_date: '',
          cheque_bank_name: '',
          cheque_branch: '',
          utr_number: '',
          payer_name: '',
          devotee_names: '',
          gotra: '',
          nakshatra: '',
          rashi: '',
          special_request: ''
        });
      }, 2000);
    } catch (err) {
      console.error('Booking error:', err);
      
      // Handle FastAPI validation errors (422) - detail is an array of error objects
      let errorMessage = 'Failed to book seva';
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // FastAPI validation error - extract messages from array
          errorMessage = detail.map(err => {
            const field = err.loc ? err.loc.join('.') : 'field';
            return `${field}: ${err.msg || 'Invalid value'}`;
          }).join('; ');
        } else if (typeof detail === 'string') {
          // Simple string error
          errorMessage = detail;
        } else {
          // Object error - convert to string
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
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
          onClose={(event, reason) => {
            // NEVER close on backdrop click - completely prevent it
            if (reason === 'backdropClick') {
              // Completely ignore backdrop clicks
              return;
            }
            // Only allow ESC if form is completely empty
            if (reason === 'escapeKeyDown') {
              if (!bookingForm.devotee_id && !mobileNumber && !bookingForm.amount_paid) {
                setBookingDialogOpen(false);
              }
              return;
            }
            // Only close if explicitly requested via Cancel button
            setBookingDialogOpen(false);
          }}
          maxWidth="sm"
          fullWidth
          disableEscapeKeyDown={true} // Always disable ESC to prevent accidental closing
          // Use slotProps for Material-UI v5 to prevent backdrop clicks from closing
          slotProps={{
            backdrop: {
              onClick: (e) => {
                // Explicitly prevent backdrop clicks from closing
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
              },
              onMouseDown: (e) => {
                // Prevent mouse down events on backdrop
                e.preventDefault();
                e.stopPropagation();
              }
            }
          }}
          // Wrap content in a container that prevents backdrop clicks
          PaperProps={{
            onClick: (e) => {
              // Prevent clicks inside paper from propagating to backdrop
              e.stopPropagation();
            },
            onMouseDown: (e) => {
              // Prevent mouse down events from propagating
              e.stopPropagation();
            }
          }}
        >
          <Box
            onClick={(e) => {
              // Prevent any clicks inside dialog from closing it
              e.stopPropagation();
            }}
            onMouseDown={(e) => {
              // Prevent mouse down events from propagating
              e.stopPropagation();
            }}
            sx={{ width: '100%' }}
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
          <DialogContent 
            dividers
            sx={{ 
              maxHeight: '70vh',
              overflowY: 'auto',
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: '#f1f1f1',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#888',
                borderRadius: '4px',
              },
            }}
          >
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

            <Stack spacing={2} sx={{ pb: 2 }}>
              {/* Mobile Number Search - Always visible at top */}
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  Devotee Mobile Number *
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    select
                    label="Country Code"
                    value={countryCode}
                    onChange={(e) => setCountryCode(e.target.value)}
                    size="small"
                    sx={{ minWidth: 120 }}
                  >
                    <MenuItem value="+91">+91 (India)</MenuItem>
                    <MenuItem value="+1">+1 (USA)</MenuItem>
                    <MenuItem value="+44">+44 (UK)</MenuItem>
                    <MenuItem value="+971">+971 (UAE)</MenuItem>
                    <MenuItem value="+65">+65 (Singapore)</MenuItem>
                  </TextField>
                  <TextField
                    label="Mobile Number"
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value.replace(/\D/g, ''))}
                    placeholder={countryCode === '+91' ? "Enter 10-digit mobile" : "Enter mobile number"}
                    fullWidth
                    inputProps={{ 
                      maxLength: countryCode === '+91' ? 10 : 15 
                    }}
                  />
                  <Button
                    variant="contained"
                    onClick={handleSearchByMobile}
                    disabled={
                      searchingDevotee || 
                      (countryCode === '+91' && mobileNumber.length !== 10) ||
                      (countryCode !== '+91' && mobileNumber.length < 7)
                    }
                    sx={{ minWidth: 100 }}
                  >
                    {searchingDevotee ? <CircularProgress size={24} /> : 'Search'}
                  </Button>
                </Box>
                {foundDevotee && (
                  <Alert severity="success" sx={{ mt: 1 }}>
                    ✅ Devotee Found: {foundDevotee.name || `${foundDevotee.first_name || ''} ${foundDevotee.last_name || ''}`.trim()}
                  </Alert>
                )}
                {showNewDevoteeForm && !foundDevotee && (
                  <Alert severity="info" sx={{ mt: 1 }}>
                    ℹ️ Devotee not found. Please fill details below to create new devotee.
                  </Alert>
                )}
              </Box>

              {/* Devotee Details - Auto-filled if found, editable if not */}
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                  Devotee Details
                </Typography>
                <Stack spacing={2}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      select
                      label="Prefix"
                      value={foundDevotee ? (foundDevotee.name_prefix || '') : (newDevoteeData.name_prefix || '')}
                      onChange={(e) => {
                        if (foundDevotee) {
                          // Update found devotee data (will be saved on submit)
                          setBookingForm({ ...bookingForm, devotee_prefix: e.target.value });
                        } else {
                          setNewDevoteeData({ ...newDevoteeData, name_prefix: e.target.value });
                        }
                      }}
                      size="small"
                      sx={{ minWidth: 100 }}
                    >
                      <MenuItem value="">None</MenuItem>
                      <MenuItem value="Mr.">Mr.</MenuItem>
                      <MenuItem value="Mrs.">Mrs.</MenuItem>
                      <MenuItem value="Ms.">Ms.</MenuItem>
                      <MenuItem value="M/s">M/s</MenuItem>
                      <MenuItem value="Dr.">Dr.</MenuItem>
                      <MenuItem value="Shri">Shri</MenuItem>
                      <MenuItem value="Smt.">Smt.</MenuItem>
                    </TextField>
                    <TextField
                      label="First Name *"
                      value={foundDevotee ? (foundDevotee.first_name || foundDevotee.name?.split(' ')[0] || '') : newDevoteeData.first_name}
                      onChange={(e) => {
                        if (!foundDevotee) {
                          setNewDevoteeData({ ...newDevoteeData, first_name: e.target.value });
                        }
                      }}
                      fullWidth
                      size="small"
                      disabled={!!foundDevotee}
                      placeholder={foundDevotee ? "Auto-filled from devotee record" : "Enter first name"}
                    />
                    <TextField
                      label="Last Name"
                      value={foundDevotee ? (foundDevotee.last_name || foundDevotee.name?.split(' ').slice(1).join(' ') || '') : newDevoteeData.last_name}
                      onChange={(e) => {
                        if (!foundDevotee) {
                          setNewDevoteeData({ ...newDevoteeData, last_name: e.target.value });
                        }
                      }}
                      fullWidth
                      size="small"
                      disabled={!!foundDevotee}
                      placeholder={foundDevotee ? "Auto-filled from devotee record" : "Enter last name"}
                    />
                  </Box>
                  <TextField
                    label="Address"
                    value={foundDevotee ? (foundDevotee.address || '') : newDevoteeData.address}
                    onChange={(e) => {
                      if (!foundDevotee) {
                        setNewDevoteeData({ ...newDevoteeData, address: e.target.value });
                      }
                    }}
                    fullWidth
                    size="small"
                    disabled={!!foundDevotee}
                    placeholder={foundDevotee ? "Auto-filled from devotee record" : "Enter address"}
                  />
                  <TextField
                    label="PIN Code"
                    value={foundDevotee ? (foundDevotee.pincode || '') : newDevoteeData.pincode}
                    onChange={(e) => {
                      if (!foundDevotee) {
                        handlePincodeChange(e.target.value);
                      }
                    }}
                    size="small"
                    inputProps={{ maxLength: 6 }}
                    fullWidth
                    disabled={!!foundDevotee}
                    placeholder={foundDevotee ? "Auto-filled from devotee record" : "Enter 6-digit PIN code"}
                    helperText={!foundDevotee && (lookingUpPincode ? 'Looking up...' : (newDevoteeData.pincode && newDevoteeData.pincode.length === 6 ? 'Auto-fills city/state below' : 'Enter 6-digit PIN code'))}
                    InputProps={{
                      endAdornment: !foundDevotee && lookingUpPincode ? <CircularProgress size={16} /> : null
                    }}
                  />
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      label="City"
                      value={foundDevotee ? (foundDevotee.city || '') : newDevoteeData.city}
                      onChange={(e) => {
                        if (!foundDevotee) {
                          setNewDevoteeData({ ...newDevoteeData, city: e.target.value });
                        }
                      }}
                      size="small"
                      sx={{ flex: 1 }}
                      disabled={!!foundDevotee}
                      placeholder={foundDevotee ? "Auto-filled from devotee record" : "Enter city"}
                      helperText={!foundDevotee && newDevoteeData.city ? '✓ Auto-filled' : ''}
                    />
                    <TextField
                      label="State"
                      value={foundDevotee ? (foundDevotee.state || '') : newDevoteeData.state}
                      onChange={(e) => {
                        if (!foundDevotee) {
                          setNewDevoteeData({ ...newDevoteeData, state: e.target.value });
                        }
                      }}
                      size="small"
                      sx={{ flex: 1 }}
                      disabled={!!foundDevotee}
                      placeholder={foundDevotee ? "Auto-filled from devotee record" : "Enter state"}
                      helperText={!foundDevotee && newDevoteeData.state ? '✓ Auto-filled' : ''}
                    />
                  </Box>
                  {!foundDevotee && (
                    <Button
                      variant="outlined"
                      onClick={handleCreateDevotee}
                      disabled={!newDevoteeData.first_name || searchingDevotee}
                      fullWidth
                    >
                      {searchingDevotee ? <CircularProgress size={24} /> : 'Create Devotee'}
                    </Button>
                  )}
                </Stack>
              </Box>

              {/* Seva Booking Details - Always visible */}
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#FF9933' }}>
                  Seva Booking Details
                </Typography>
                <Stack spacing={2}>
                  <TextField
                    label="Booking Date *"
                    type="date"
                    value={bookingForm.booking_date}
                    onChange={(e) => setBookingForm({...bookingForm, booking_date: e.target.value})}
                    InputLabelProps={{ shrink: true }}
                    inputProps={{ min: new Date().toISOString().split('T')[0] }}
                    fullWidth
                    size="small"
                  />

                  {selectedSeva?.time_slot && (
                    <TextField
                      label="Preferred Time"
                      value={bookingForm.booking_time}
                      onChange={(e) => setBookingForm({...bookingForm, booking_time: e.target.value})}
                      helperText={`Recommended: ${selectedSeva.time_slot}`}
                      fullWidth
                      size="small"
                    />
                  )}

                  <TextField
                    label="Amount *"
                    type="number"
                    value={bookingForm.amount_paid}
                    onChange={(e) => setBookingForm({...bookingForm, amount_paid: parseFloat(e.target.value)})}
                    InputProps={{
                      startAdornment: '₹'
                    }}
                    fullWidth
                    size="small"
                  />

                  <FormControl fullWidth size="small">
                    <InputLabel>Payment Method *</InputLabel>
                    <Select
                      value={bookingForm.payment_method}
                      onChange={(e) => setBookingForm({...bookingForm, payment_method: e.target.value})}
                      label="Payment Method *"
                    >
                      <MenuItem value="Cash">Cash</MenuItem>
                      <MenuItem value="UPI">UPI</MenuItem>
                      <MenuItem value="Card">Card</MenuItem>
                      <MenuItem value="Cheque">Cheque</MenuItem>
                      <MenuItem value="Online">Online Transfer</MenuItem>
                    </Select>
                  </FormControl>
                  
                  {/* Payment-specific fields */}
                  {bookingForm.payment_method === 'UPI' && (
                    <>
                      <TextField
                        fullWidth
                        label="Sender UPI ID"
                        value={bookingForm.sender_upi_id || ''}
                        onChange={(e) => setBookingForm({...bookingForm, sender_upi_id: e.target.value})}
                        placeholder="9876543210@paytm"
                        helperText="From SMS notification (e.g., VPA)"
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="UPI Reference Number"
                        value={bookingForm.upi_reference_number || ''}
                        onChange={(e) => setBookingForm({...bookingForm, upi_reference_number: e.target.value})}
                        placeholder="UTR/RRN from SMS"
                        helperText="Transaction reference from SMS"
                        size="small"
                      />
                    </>
                  )}
                  
                  {bookingForm.payment_method === 'Cheque' && (
                    <>
                      <TextField
                        fullWidth
                        label="Cheque Number *"
                        value={bookingForm.cheque_number || ''}
                        onChange={(e) => setBookingForm({...bookingForm, cheque_number: e.target.value})}
                        required
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="Cheque Date *"
                        type="date"
                        value={bookingForm.cheque_date || ''}
                        onChange={(e) => setBookingForm({...bookingForm, cheque_date: e.target.value})}
                        required
                        InputLabelProps={{ shrink: true }}
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="Bank Name *"
                        value={bookingForm.cheque_bank_name || ''}
                        onChange={(e) => setBookingForm({...bookingForm, cheque_bank_name: e.target.value})}
                        required
                        placeholder="e.g., SBI, HDFC"
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="Branch"
                        value={bookingForm.cheque_branch || ''}
                        onChange={(e) => setBookingForm({...bookingForm, cheque_branch: e.target.value})}
                        placeholder="Branch name"
                        size="small"
                      />
                    </>
                  )}
                  
                  {bookingForm.payment_method === 'Online' && (
                    <>
                      <TextField
                        fullWidth
                        label="UTR Number *"
                        value={bookingForm.utr_number || ''}
                        onChange={(e) => setBookingForm({...bookingForm, utr_number: e.target.value})}
                        required
                        placeholder="Unique Transfer Reference"
                        helperText="UTR or transaction reference from bank"
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="Payer Name"
                        value={bookingForm.payer_name || ''}
                        onChange={(e) => setBookingForm({...bookingForm, payer_name: e.target.value})}
                        placeholder="Name of person who made the transfer"
                        helperText="May be different from devotee/seva kartha name"
                        size="small"
                      />
                    </>
                  )}

                  <TextField
                    label="Additional Devotee Names"
                    value={bookingForm.devotee_names}
                    onChange={(e) => setBookingForm({...bookingForm, devotee_names: e.target.value})}
                    placeholder="Names for whom seva is performed (comma separated)"
                    multiline
                    rows={2}
                    fullWidth
                    size="small"
                  />

                  <FormControl fullWidth size="small">
                    <InputLabel>Gotra</InputLabel>
                    <Select
                      value={bookingForm.gotra}
                      onChange={(e) => setBookingForm({...bookingForm, gotra: e.target.value})}
                      label="Gotra"
                    >
                      <MenuItem value=""><em>Select Gotra</em></MenuItem>
                      {dropdownOptions.gothras && dropdownOptions.gothras.length > 0 ? (
                        dropdownOptions.gothras.map((gotra) => (
                          <MenuItem key={gotra} value={gotra}>{gotra}</MenuItem>
                        ))
                      ) : (
                        <MenuItem disabled>Loading...</MenuItem>
                      )}
                    </Select>
                  </FormControl>

                  <FormControl fullWidth size="small">
                    <InputLabel>Nakshatra</InputLabel>
                    <Select
                      value={bookingForm.nakshatra}
                      onChange={(e) => setBookingForm({...bookingForm, nakshatra: e.target.value})}
                      label="Nakshatra"
                    >
                      <MenuItem value=""><em>Select Nakshatra</em></MenuItem>
                      {dropdownOptions.nakshatras && dropdownOptions.nakshatras.length > 0 ? (
                        dropdownOptions.nakshatras.map((nakshatra) => (
                          <MenuItem key={nakshatra} value={nakshatra}>{nakshatra}</MenuItem>
                        ))
                      ) : (
                        <MenuItem disabled>Loading...</MenuItem>
                      )}
                    </Select>
                  </FormControl>

                  <FormControl fullWidth size="small">
                    <InputLabel>Rashi</InputLabel>
                    <Select
                      value={bookingForm.rashi}
                      onChange={(e) => setBookingForm({...bookingForm, rashi: e.target.value})}
                      label="Rashi"
                    >
                      <MenuItem value=""><em>Select Rashi</em></MenuItem>
                      {dropdownOptions.rashis && dropdownOptions.rashis.length > 0 ? (
                        dropdownOptions.rashis.map((rashi) => (
                          <MenuItem key={rashi} value={rashi}>{rashi}</MenuItem>
                        ))
                      ) : (
                        <MenuItem disabled>Loading...</MenuItem>
                      )}
                    </Select>
                  </FormControl>

                  <TextField
                    label="Special Request / Instructions"
                    value={bookingForm.special_request}
                    onChange={(e) => setBookingForm({...bookingForm, special_request: e.target.value})}
                    multiline
                    rows={3}
                    fullWidth
                    size="small"
                  />
                </Stack>
              </Box>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button 
              onClick={() => {
                // Reset form when canceling
                setBookingDialogOpen(false);
                setMobileNumber('');
                setCountryCode('+91');
                setFoundDevotee(null);
                setShowNewDevoteeForm(false);
                setBookingError(null);
                setBookingSuccess(false);
                setNewDevoteeData({
                  first_name: '',
                  last_name: '',
                  name_prefix: '',
                  address: '',
                  pincode: '',
                  city: '',
                  state: '',
                  country: 'India'
                });
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleBookingSubmit}
              variant="contained"
              disabled={!bookingForm.devotee_id || !bookingForm.amount_paid || bookingSuccess}
            >
              Confirm Booking
            </Button>
          </DialogActions>
          </Box>
        </Dialog>
      </Box>
  );
}

export default Sevas;
