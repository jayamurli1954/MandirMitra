import React, { useState } from 'react';
import {
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import GenerateIcon from '@mui/icons-material/AccountTree';
import DownloadIcon from '@mui/icons-material/Download';
import Layout from '../components/Layout';
import api from '../services/api';

function Kundli() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [kundliData, setKundliData] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    birthDate: '',
    birthTime: '12:00',
    latitude: '12.9716', // Default to Bangalore
    longitude: '77.5946',
    templeName: '',
    templeLogoUrl: '',
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    setKundliData(null);

    try {
      // Validate inputs
      if (!formData.name || !formData.birthDate || !formData.birthTime) {
        setError('Please fill in all required fields: Name, Birth Date, and Birth Time');
        setLoading(false);
        return;
      }

      // Parse and format datetime
      const birthDateTime = `${formData.birthDate}T${formData.birthTime}:00`;
      const lat = parseFloat(formData.latitude);
      const lon = parseFloat(formData.longitude);

      if (isNaN(lat) || isNaN(lon)) {
        setError('Please enter valid latitude and longitude');
        setLoading(false);
        return;
      }

      // Call API
      const response = await api.post('/api/v1/panchang/kundli/generate', {
        birth_datetime: birthDateTime,
        latitude: lat,
        longitude: lon,
        name: formData.name,
        temple_name: formData.templeName || undefined,
        temple_logo_url: formData.templeLogoUrl || undefined,
      });

      if (response.data.success) {
        setKundliData(response.data.kundli);
        setSuccess('Kundli generated successfully!');
      } else {
        setError('Failed to generate Kundli. Please try again.');
      }
    } catch (err) {
      console.error('Error generating Kundli:', err);
      let errorMsg = 'Failed to generate Kundli';
      
      if (err?.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err?.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err?.message) {
        errorMsg = err.message;
      } else if (err?.code === 'ERR_NETWORK' || err?.message?.includes('Network Error')) {
        errorMsg = 'Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000';
      }
      
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (!kundliData?.html) {
      setError('No Kundli data available to download');
      return;
    }

    // Create a new window with the HTML content
    const printWindow = window.open('', '_blank');
    printWindow.document.write(kundliData.html);
    printWindow.document.close();
    
    // Trigger print dialog
    setTimeout(() => {
      printWindow.print();
    }, 500);
  };

  return (
    <Layout>
      <Box>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', mb: 3 }}>
          📿 Janma Kundli (Birth Chart)
        </Typography>

        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            ⚠️ Known Issues - Under Review
          </Typography>
          <Typography variant="body2">
            This page has been flagged for the following issues:
            <ul style={{ marginTop: '8px', marginBottom: '0', paddingLeft: '20px' }}>
              <li>Report generation is not correct</li>
              <li>Horoscope chart style needs correction</li>
            </ul>
            Please use with caution until these issues are resolved.
          </Typography>
        </Alert>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Form Section */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Birth Details
              </Typography>
              <form onSubmit={handleGenerate}>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Birth Date"
                      name="birthDate"
                      type="date"
                      value={formData.birthDate}
                      onChange={handleInputChange}
                      required
                      InputLabelProps={{ shrink: true }}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Birth Time (IST)"
                      name="birthTime"
                      type="time"
                      value={formData.birthTime}
                      onChange={handleInputChange}
                      required
                      InputLabelProps={{ shrink: true }}
                      variant="outlined"
                      helperText="Enter time in 24-hour format"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Latitude"
                      name="latitude"
                      value={formData.latitude}
                      onChange={handleInputChange}
                      required
                      type="number"
                      inputProps={{ step: '0.0001' }}
                      variant="outlined"
                      helperText="e.g., 12.9716 for Bangalore"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Longitude"
                      name="longitude"
                      value={formData.longitude}
                      onChange={handleInputChange}
                      required
                      type="number"
                      inputProps={{ step: '0.0001' }}
                      variant="outlined"
                      helperText="e.g., 77.5946 for Bangalore"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Temple Name (Optional)"
                      name="templeName"
                      value={formData.templeName}
                      onChange={handleInputChange}
                      variant="outlined"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Temple Logo URL (Optional)"
                      name="templeLogoUrl"
                      value={formData.templeLogoUrl}
                      onChange={handleInputChange}
                      variant="outlined"
                      helperText="URL of temple logo for PDF header"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button
                      type="submit"
                      variant="contained"
                      fullWidth
                      size="large"
                      startIcon={loading ? <CircularProgress size={20} /> : <GenerateIcon />}
                      disabled={loading}
                      sx={{ py: 1.5 }}
                    >
                      {loading ? 'Generating...' : 'Generate Kundli'}
                    </Button>
                  </Grid>
                </Grid>
              </form>
            </Paper>
          </Grid>

          {/* Results Section */}
          <Grid item xs={12} md={8}>
            {kundliData ? (
              <Paper sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Generated Kundli
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadPDF}
                  >
                    Download PDF
                  </Button>
                </Box>

                <Divider sx={{ mb: 3 }} />

                {/* Lagna Information */}
                {kundliData.lagna_rashi && (
                  <Card sx={{ mb: 2, bgcolor: '#E8F5E9' }}>
                    <CardContent>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                        Lagna (Ascendant)
                      </Typography>
                      <Typography variant="body1">{kundliData.lagna_rashi}</Typography>
                    </CardContent>
                  </Card>
                )}

                {/* Dasha Information */}
                {kundliData.dasha && kundliData.dasha.length > 0 && (
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                        Vimshottari Dasha (120 Years)
                      </Typography>
                      <Box sx={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                          <thead>
                            <tr style={{ backgroundColor: '#ffd700' }}>
                              <th style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                Mahadasha
                              </th>
                              <th style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                Start Date
                              </th>
                              <th style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                End Date
                              </th>
                              <th style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                Duration
                              </th>
                            </tr>
                          </thead>
                          <tbody>
                            {kundliData.dasha.map((dasha, idx) => (
                              <tr key={idx} style={{ backgroundColor: idx % 2 === 0 ? '#fffef5' : '#fff' }}>
                                <td style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center', fontWeight: 'bold' }}>
                                  {dasha.lord}
                                </td>
                                <td style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                  {dasha.start}
                                </td>
                                <td style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                  {dasha.end}
                                </td>
                                <td style={{ padding: '8px', border: '1px solid #8b4513', textAlign: 'center' }}>
                                  {dasha.years} yrs
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </Box>
                    </CardContent>
                  </Card>
                )}

                {/* Charts Preview */}
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                      Charts (Rasi & Navamsa)
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Click "Download PDF" to view the complete Kundli with Rasi Chart (D1), Navamsa Chart (D9), and full details.
                    </Typography>
                    {kundliData.html && (
                      <Alert severity="info">
                        Kundli HTML generated successfully. Use the Download PDF button to view or print the complete chart.
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              </Paper>
            ) : (
              <Paper sx={{ p: 3, textAlign: 'center', bgcolor: '#f5f5f5' }}>
                <Typography variant="body1" color="text.secondary">
                  Enter birth details and click "Generate Kundli" to create your birth chart.
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
}

export default Kundli;


