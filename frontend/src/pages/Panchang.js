import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import Layout from '../components/Layout';
import PanchangDisplay from '../components/PanchangDisplay';
import api from '../services/api';

function Panchang() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [settings, setSettings] = useState(null);
  const [panchangData, setPanchangData] = useState(null);

  useEffect(() => {
    fetchPanchangData();
  }, []);

  const fetchPanchangData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch panchang display settings and data
      const [settingsRes, panchangRes] = await Promise.allSettled([
        api.get('/api/v1/panchang/display-settings/'),
        api.get('/api/v1/panchang/today'),
      ]);
      
      if (settingsRes.status === 'fulfilled' && settingsRes.value.data) {
        setSettings(settingsRes.value.data);
      } else if (settingsRes.status === 'rejected') {
        console.log('Settings API failed:', settingsRes.reason);
      }
      
      if (panchangRes.status === 'fulfilled' && panchangRes.value.data) {
        setPanchangData(panchangRes.value.data);
      } else if (panchangRes.status === 'rejected') {
        const error = panchangRes.reason;
        let errorMsg = 'Unknown error';
        
        if (error?.response?.data?.detail) {
          errorMsg = error.response.data.detail;
        } else if (error?.response?.data?.message) {
          errorMsg = error.response.data.message;
        } else if (error?.message) {
          errorMsg = error.message;
        } else if (error?.code === 'ERR_NETWORK' || error?.message?.includes('Network Error')) {
          errorMsg = 'Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000';
        }
        
        console.error('Panchang API error:', error);
        setError(`Failed to load panchang data: ${errorMsg}`);
      }
    } catch (err) {
      console.error('Error fetching panchang data:', err);
      let errorMsg = 'Unknown error';
      
      if (err?.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err?.response?.data?.message) {
        errorMsg = err.response.data.message;
      } else if (err?.message) {
        errorMsg = err.message;
      } else if (err?.code === 'ERR_NETWORK' || err?.message?.includes('Network Error')) {
        errorMsg = 'Cannot connect to backend server. Please ensure the backend is running on http://localhost:8000';
      }
      
      setError(`Failed to load panchang data: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Today's Panchang
        </Typography>
        <Button
          variant="outlined"
          startIcon={<SettingsIcon />}
          onClick={() => window.location.href = '/settings'}
        >
          Display Settings
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {settings && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: '#FFF3E0' }}>
          <Typography variant="body2" color="text.secondary">
            Display Mode: <strong>{settings.display_mode}</strong> | 
            Language: <strong>{settings.primary_language}</strong> | 
            Show on Dashboard: <strong>{settings.show_on_dashboard ? 'Yes' : 'No'}</strong>
          </Typography>
        </Paper>
      )}

      {/* Full Panchang Display */}
      <PanchangDisplay 
        data={panchangData} 
        settings={settings}
        compact={false}
      />
    </Layout>
  );
}

export default Panchang;

