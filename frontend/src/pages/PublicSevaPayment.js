import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Container, Paper, Typography, TextField, MenuItem,
  Button, Stepper, Step, StepLabel, Divider, Alert,
  CircularProgress, Chip, Grid, InputAdornment, ToggleButton, ToggleButtonGroup,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import WhatsAppIcon from '@mui/icons-material/WhatsApp';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import VolunteerActivismIcon from '@mui/icons-material/VolunteerActivism';
import TempleHinduIcon from '@mui/icons-material/TempleHindu';
import { buildApiUrl } from '../utils/apiBaseUrl';

const GOTHRA_OPTIONS = [
  'Kashyapa', 'Bharadvaja', 'Vasishtha', 'Vishvamitra', 'Jamadagni',
  'Gautama', 'Atri', 'Agastya', 'Angirasa', 'Kaundinya',
  'Parashara', 'Garga', 'Sandilya', 'Vatsa', 'Other',
];

const NAKSHTRA_OPTIONS = [
  'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
  'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni',
  'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha',
  'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha',
  'Shravana', 'Dhanishtha', 'Shatabhisha', 'Purva Bhadrapada',
  'Uttara Bhadrapada', 'Revati',
];

const RASHI_OPTIONS = [
  'Mesha (Aries)', 'Vrishabha (Taurus)', 'Mithuna (Gemini)',
  'Karka (Cancer)', 'Simha (Leo)', 'Kanya (Virgo)',
  'Tula (Libra)', 'Vrishchika (Scorpio)', 'Dhanu (Sagittarius)',
  'Makara (Capricorn)', 'Kumbha (Aquarius)', 'Meena (Pisces)',
];

const STEPS = ['Select', 'Devotee Details', 'Make Payment'];

export default function PublicSevaPayment() {
  const params = new URLSearchParams(window.location.search);
  const templeId = params.get('temple_id') || '3';

  const [activeStep, setActiveStep] = useState(0);
  const [paymentType, setPaymentType] = useState('seva'); // 'seva' | 'donation'
  const [templeInfo, setTempleInfo] = useState(null);
  const [sevas, setSevas] = useState([]);
  const [donationCategories, setDonationCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [paymentResult, setPaymentResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [pincodeLoading, setPincodeLoading] = useState(false);
  const [mobileSearching, setMobileSearching] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    // selection fields (seva or donation)
    seva_id: '', seva_name: '', amount: '',
    category_id: '', category_name: '',
    // devotee fields
    phone: '', name: '', email: '', address: '',
    pincode: '', city: '', state: '',
    // astrological (seva only)
    gothra: '', nakshtra: '', rashi: '',
  });

  useEffect(() => {
    const load = async () => {
      try {
        const [infoRes, sevasRes, donationsRes] = await Promise.all([
          fetch(buildApiUrl(`/api/v1/mandirmitra/public/temples/${templeId}/info`)),
          fetch(buildApiUrl(`/api/v1/mandirmitra/public/temples/${templeId}/sevas`)),
          fetch(buildApiUrl(`/api/v1/mandirmitra/public/temples/${templeId}/donation-categories`)),
        ]);
        if (infoRes.ok) setTempleInfo(await infoRes.json());
        if (sevasRes.ok) setSevas(await sevasRes.json());
        if (donationsRes.ok) setDonationCategories(await donationsRes.json());
      } catch (e) {
        setError('Unable to load temple information. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [templeId]);

  const handleSevaSelect = (seva) => {
    setForm((f) => ({
      ...f,
      seva_id: seva.seva_id,
      seva_name: seva.seva_name,
      amount: seva.amount || '',
      category_id: '',
      category_name: '',
    }));
  };

  const handleDonationSelect = (cat) => {
    setForm((f) => ({
      ...f,
      category_id: cat.id,
      category_name: cat.name,
      amount: '',
      seva_id: '',
      seva_name: '',
    }));
  };

  const handlePaymentTypeChange = (_, newType) => {
    if (!newType) return;
    setPaymentType(newType);
    setForm((f) => ({
      ...f,
      seva_id: '', seva_name: '',
      category_id: '', category_name: '',
      amount: '',
      gothra: '', nakshtra: '', rashi: '',
    }));
  };

  const handleMobileBlur = useCallback(async () => {
    if (form.phone.length < 10) return;
    setMobileSearching(true);
    try {
      const res = await fetch(
        buildApiUrl(`/api/v1/mandirmitra/public/temples/${templeId}/devotee/autofill/${form.phone}`)
      );
      if (res.ok) {
        const data = await res.json();
        if (data.found && data.devotee) {
          setForm((f) => ({ ...f, ...data.devotee }));
        }
      }
    } catch (_) {}
    finally { setMobileSearching(false); }
  }, [form.phone, templeId]);

  const handlePincodeBlur = useCallback(async () => {
    if (form.pincode.length !== 6) return;
    setPincodeLoading(true);
    try {
      const res = await fetch(buildApiUrl(`/api/v1/mandirmitra/public/location/pincode/${form.pincode}`));
      if (res.ok) {
        const data = await res.json();
        if (data.found) {
          setForm((f) => ({ ...f, city: data.city, state: data.state }));
        }
      }
    } catch (_) {}
    finally { setPincodeLoading(false); }
  }, [form.pincode]);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');
    try {
      const body = {
        payment_type: paymentType,
        phone: form.phone,
        name: form.name,
        email: form.email,
        address: form.address,
        pincode: form.pincode,
        city: form.city,
        state: form.state,
        amount: form.amount,
        ...(paymentType === 'seva'
          ? {
              seva_id: form.seva_id,
              seva_name: form.seva_name,
              gothra: form.gothra,
              nakshtra: form.nakshtra,
              rashi: form.rashi,
            }
          : {
              category_id: form.category_id,
              category_name: form.category_name,
            }),
      };

      const res = await fetch(
        buildApiUrl(`/api/v1/mandirmitra/public/temples/${templeId}/seva-payments`),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || 'Submission failed. Please try again.');
        return;
      }
      setPaymentResult(data);
      setActiveStep(2);
    } catch (_) {
      setError('Network error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const resetForm = () => {
    setActiveStep(0);
    setPaymentResult(null);
    setPaymentType('seva');
    setForm({
      seva_id: '', seva_name: '', amount: '',
      category_id: '', category_name: '',
      phone: '', name: '', email: '', address: '',
      pincode: '', city: '', state: '',
      gothra: '', nakshtra: '', rashi: '',
    });
  };

  const step0Valid = paymentType === 'seva' ? !!form.seva_name : !!form.category_name;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#FFF8F0', py: 3 }}>
      <Container maxWidth="sm">
        {/* Temple Header */}
        <Paper elevation={2} sx={{ p: 2, mb: 3, textAlign: 'center', bgcolor: '#FF9933' }}>
          <Typography variant="h6" fontWeight="bold" color="white">
            {templeInfo?.trust_name || templeInfo?.temple_name || 'Temple Payment'}
          </Typography>
          {templeInfo?.temple_name && templeInfo?.trust_name && (
            <Typography variant="body2" color="white" sx={{ opacity: 0.9 }}>
              {templeInfo.temple_name}
            </Typography>
          )}
        </Paper>

        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {STEPS.map((label) => (
            <Step key={label}><StepLabel>{label}</StepLabel></Step>
          ))}
        </Stepper>

        {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

        {/* STEP 0 — Select Payment Type + Item */}
        {activeStep === 0 && (
          <Paper elevation={1} sx={{ p: 3 }}>
            {/* Payment type toggle */}
            <Box display="flex" justifyContent="center" mb={3}>
              <ToggleButtonGroup
                value={paymentType}
                exclusive
                onChange={handlePaymentTypeChange}
                color="primary"
                size="small"
              >
                <ToggleButton value="seva" sx={{ px: 3, gap: 0.5 }}>
                  <TempleHinduIcon fontSize="small" />
                  Book a Seva
                </ToggleButton>
                <ToggleButton value="donation" sx={{ px: 3, gap: 0.5 }}>
                  <VolunteerActivismIcon fontSize="small" />
                  Make a Donation
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* SEVA selection */}
            {paymentType === 'seva' && (
              <>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">Select Seva</Typography>
                {sevas.length === 0 ? (
                  <Alert severity="info">No sevas available at this time.</Alert>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    {sevas.map((seva) => (
                      <Paper
                        key={seva.seva_id}
                        variant="outlined"
                        onClick={() => handleSevaSelect(seva)}
                        sx={{
                          p: 2, cursor: 'pointer',
                          border: form.seva_id === seva.seva_id ? '2px solid #FF9933' : '1px solid #ddd',
                          bgcolor: form.seva_id === seva.seva_id ? '#FFF3E0' : 'white',
                        }}
                      >
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography fontWeight={form.seva_id === seva.seva_id ? 'bold' : 'normal'}>
                            {seva.seva_name}
                          </Typography>
                          {seva.amount > 0 && (
                            <Chip label={`₹${seva.amount}`} color="primary" size="small" />
                          )}
                        </Box>
                        {seva.description && (
                          <Typography variant="caption" color="text.secondary">{seva.description}</Typography>
                        )}
                        {seva.frequency === 'annual' && (
                          <Chip label="Annual" size="small" sx={{ mt: 0.5 }} color="warning" variant="outlined" />
                        )}
                      </Paper>
                    ))}
                  </Box>
                )}
                {form.seva_name && (
                  <TextField
                    label="Amount (₹)"
                    value={form.amount}
                    onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                    fullWidth
                    sx={{ mt: 2 }}
                    type="number"
                    helperText="You can edit the amount if needed"
                  />
                )}
              </>
            )}

            {/* DONATION category selection */}
            {paymentType === 'donation' && (
              <>
                <Typography variant="subtitle1" gutterBottom fontWeight="bold">Select Donation Category</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {donationCategories.map((cat) => (
                    <Paper
                      key={cat.id}
                      variant="outlined"
                      onClick={() => handleDonationSelect(cat)}
                      sx={{
                        p: 2, cursor: 'pointer',
                        border: form.category_id === cat.id ? '2px solid #FF9933' : '1px solid #ddd',
                        bgcolor: form.category_id === cat.id ? '#FFF3E0' : 'white',
                      }}
                    >
                      <Typography fontWeight={form.category_id === cat.id ? 'bold' : 'normal'}>
                        {cat.name}
                      </Typography>
                      {cat.description && (
                        <Typography variant="caption" color="text.secondary">{cat.description}</Typography>
                      )}
                    </Paper>
                  ))}
                </Box>
                {form.category_name && (
                  <TextField
                    label="Donation Amount (₹) *"
                    value={form.amount}
                    onChange={(e) => setForm((f) => ({ ...f, amount: e.target.value }))}
                    fullWidth
                    sx={{ mt: 2 }}
                    type="number"
                    required
                  />
                )}
              </>
            )}

            <Button
              variant="contained"
              fullWidth
              sx={{ mt: 3, bgcolor: '#FF9933' }}
              disabled={!step0Valid || (paymentType === 'donation' && !form.amount)}
              onClick={() => setActiveStep(1)}
            >
              Continue
            </Button>
          </Paper>
        )}

        {/* STEP 1 — Devotee Details */}
        {activeStep === 1 && (
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom fontWeight="bold">Devotee Details</Typography>
            {paymentType === 'seva' ? (
              <Alert severity="info" sx={{ mb: 2 }} icon={<TempleHinduIcon />}>
                <strong>Seva:</strong> {form.seva_name}
                {form.amount && ` — ₹${form.amount}`}
              </Alert>
            ) : (
              <Alert severity="success" sx={{ mb: 2 }} icon={<VolunteerActivismIcon />}>
                <strong>Donation:</strong> {form.category_name} — ₹{form.amount}
              </Alert>
            )}
            <Divider sx={{ mb: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  label="Mobile Number *"
                  value={form.phone}
                  onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                  onBlur={handleMobileBlur}
                  fullWidth
                  inputProps={{ maxLength: 10 }}
                  InputProps={{
                    endAdornment: mobileSearching
                      ? <InputAdornment position="end"><CircularProgress size={18} /></InputAdornment>
                      : <InputAdornment position="end"><SearchIcon color="action" /></InputAdornment>,
                  }}
                  helperText="Enter mobile to auto-fill your details if already registered"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Full Name *"
                  value={form.name}
                  onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  fullWidth
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Email"
                  value={form.email}
                  onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                  fullWidth
                  type="email"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Address"
                  value={form.address}
                  onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))}
                  fullWidth
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="Pincode"
                  value={form.pincode}
                  onChange={(e) => setForm((f) => ({ ...f, pincode: e.target.value }))}
                  onBlur={handlePincodeBlur}
                  fullWidth
                  inputProps={{ maxLength: 6 }}
                  InputProps={{
                    endAdornment: pincodeLoading
                      ? <InputAdornment position="end"><CircularProgress size={16} /></InputAdornment>
                      : null,
                  }}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="City"
                  value={form.city}
                  onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))}
                  fullWidth
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  label="State"
                  value={form.state}
                  onChange={(e) => setForm((f) => ({ ...f, state: e.target.value }))}
                  fullWidth
                />
              </Grid>

              {/* Astrological details — SEVA only */}
              {paymentType === 'seva' && (
                <>
                  <Grid item xs={12}>
                    <Divider>
                      <Typography variant="caption" color="text.secondary">
                        Astrological Details (Optional)
                      </Typography>
                    </Divider>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      select
                      label="Gothra"
                      value={form.gothra}
                      onChange={(e) => setForm((f) => ({ ...f, gothra: e.target.value }))}
                      fullWidth
                    >
                      <MenuItem value="">Select</MenuItem>
                      {GOTHRA_OPTIONS.map((g) => <MenuItem key={g} value={g}>{g}</MenuItem>)}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      select
                      label="Nakshtra"
                      value={form.nakshtra}
                      onChange={(e) => setForm((f) => ({ ...f, nakshtra: e.target.value }))}
                      fullWidth
                    >
                      <MenuItem value="">Select</MenuItem>
                      {NAKSHTRA_OPTIONS.map((n) => <MenuItem key={n} value={n}>{n}</MenuItem>)}
                    </TextField>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <TextField
                      select
                      label="Rashi"
                      value={form.rashi}
                      onChange={(e) => setForm((f) => ({ ...f, rashi: e.target.value }))}
                      fullWidth
                    >
                      <MenuItem value="">Select</MenuItem>
                      {RASHI_OPTIONS.map((r) => <MenuItem key={r} value={r}>{r}</MenuItem>)}
                    </TextField>
                  </Grid>
                </>
              )}
            </Grid>

            <Box display="flex" gap={2} mt={3}>
              <Button variant="outlined" onClick={() => setActiveStep(0)} sx={{ flex: 1 }}>Back</Button>
              <Button
                variant="contained"
                sx={{ flex: 2, bgcolor: '#FF9933' }}
                disabled={!form.phone || !form.name || submitting}
                onClick={handleSubmit}
              >
                {submitting ? <CircularProgress size={22} color="inherit" /> : 'Proceed to Payment'}
              </Button>
            </Box>
          </Paper>
        )}

        {/* STEP 2 — Payment Instructions */}
        {activeStep === 2 && paymentResult && (
          <Paper elevation={1} sx={{ p: 3 }}>
            <Box textAlign="center" mb={2}>
              <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main' }} />
              <Typography variant="h6" fontWeight="bold" mt={1}>
                Details Saved! Complete Your Payment
              </Typography>
              <Chip label={`Payment ID: ${paymentResult.payment_id}`} color="primary" sx={{ mt: 1 }} />
            </Box>
            <Divider sx={{ mb: 2 }} />

            <Alert severity="info" sx={{ mb: 2 }}>
              <strong>{paymentResult.payment_type === 'donation' ? 'Donation' : 'Seva'}:</strong>{' '}
              {paymentResult.seva_name}
              {paymentResult.amount && ` — ₹${paymentResult.amount}`}
            </Alert>

            {/* QR Code */}
            {paymentResult.qr_code_image_url && (
              <Box textAlign="center" mb={2}>
                <Typography variant="subtitle2" gutterBottom>Scan QR Code to Pay</Typography>
                <img
                  src={paymentResult.qr_code_image_url}
                  alt="Temple UPI QR Code"
                  style={{ maxWidth: 220, border: '1px solid #ddd', borderRadius: 8 }}
                />
              </Box>
            )}

            {/* UPI ID */}
            {paymentResult.upi_id && (
              <Paper variant="outlined" sx={{ p: 2, mb: 2, textAlign: 'center', bgcolor: '#F9F9F9' }}>
                <Typography variant="body2" color="text.secondary">UPI ID</Typography>
                <Typography variant="h6" fontWeight="bold" letterSpacing={0.5}>
                  {paymentResult.upi_id}
                </Typography>
                <Button
                  size="small"
                  startIcon={copied ? <CheckCircleIcon /> : <ContentCopyIcon />}
                  onClick={() => handleCopy(paymentResult.upi_id)}
                  sx={{ mt: 0.5 }}
                >
                  {copied ? 'Copied!' : 'Copy UPI ID'}
                </Button>
              </Paper>
            )}

            {/* WhatsApp Instruction */}
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2" fontWeight="bold" gutterBottom>
                After payment, send WhatsApp confirmation to temple admin:
              </Typography>
              <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                {paymentResult.whatsapp_message_template}
              </Typography>
            </Alert>

            {paymentResult.whatsapp_link && (
              <Button
                variant="contained"
                fullWidth
                startIcon={<WhatsAppIcon />}
                href={paymentResult.whatsapp_link}
                target="_blank"
                sx={{ bgcolor: '#25D366', '&:hover': { bgcolor: '#128C7E' }, mb: 2 }}
              >
                Send WhatsApp Confirmation
              </Button>
            )}

            <Button variant="outlined" fullWidth onClick={resetForm}>
              Make Another Payment
            </Button>
          </Paper>
        )}

        <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={3}>
          Powered by MandirMitra
        </Typography>
      </Container>
    </Box>
  );
}
