import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import api from '../services/api';

function Settings() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
        Settings
      </Typography>

      <Paper sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Panchang Display Settings
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Configure what panchang elements to display, language preferences, and visual settings.
        </Typography>
        <Button
          variant="contained"
          startIcon={<SettingsIcon />}
          onClick={() => navigate('/panchang')}
        >
          Configure Panchang Settings
        </Button>
      </Paper>

      <Paper sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Temple Configuration
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Temple profile, donation categories, and other settings will be available here.
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          Coming soon: Temple profile setup, donation categories management, and user preferences.
        </Alert>
      </Paper>
    </Layout>
  );
}

export default Settings;
