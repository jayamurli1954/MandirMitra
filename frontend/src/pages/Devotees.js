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
} from '@mui/material';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import Layout from '../components/Layout';
import api from '../services/api';

function Devotees() {
  const [devotees, setDevotees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDevotees();
  }, []);

  const fetchDevotees = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Try direct devotees API first
      try {
        const devoteesRes = await api.get('/api/v1/devotees');
        if (devoteesRes.data && Array.isArray(devoteesRes.data) && devoteesRes.data.length > 0) {
          setDevotees(devoteesRes.data);
          return;
        }
      } catch (devoteesErr) {
        console.log('Devotees API failed, trying donations API:', devoteesErr);
      }
      
      // Fallback: Get devotees from donations (unique by phone)
      const donationsRes = await api.get('/api/v1/donations?limit=1000');
      
      if (donationsRes.data && Array.isArray(donationsRes.data) && donationsRes.data.length > 0) {
        // Extract unique devotees from donations
        const devoteeMap = new Map();
        
        donationsRes.data.forEach(donation => {
          const phone = donation.devotee?.phone || donation.devotee_phone;
          if (phone) {
            if (!devoteeMap.has(phone)) {
              devoteeMap.set(phone, {
                id: donation.devotee?.id || phone,
                name: donation.devotee?.name || 'Unknown',
                phone: phone,
                email: donation.devotee?.email || null,
                address: donation.devotee?.address || null,
                city: donation.devotee?.city || null,
                state: donation.devotee?.state || null,
                pincode: donation.devotee?.pincode || null,
                donation_count: 0,
                total_donated: 0
              });
            }
            // Update donation stats
            const devotee = devoteeMap.get(phone);
            devotee.donation_count += 1;
            devotee.total_donated += (donation.amount || 0);
          }
        });
        
        const devoteesList = Array.from(devoteeMap.values());
        setDevotees(devoteesList);
        
        if (devoteesList.length === 0) {
          setError('No devotees found. Devotees are automatically created when donations are recorded.');
        }
      } else {
        setError('No donations found. Devotees are automatically created when donations are recorded.');
        setDevotees([]);
      }
    } catch (err) {
      console.error('Error fetching devotees:', err);
      setError(`Failed to load devotees: ${err.response?.data?.detail || err.message || 'Unknown error'}. Devotees are automatically created when donations are recorded.`);
      setDevotees([]);
    } finally {
      setLoading(false);
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
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
        Devotees
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Devotees are automatically created when donations are recorded. No need to create them separately.
      </Alert>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Paper sx={{ p: 3 }}>
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
                  <TableCell>Address</TableCell>
                  <TableCell align="right">Donations</TableCell>
                  <TableCell align="right">Total Donated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devotees.map((devotee) => (
                  <TableRow key={devotee.id || devotee.phone}>
                    <TableCell>
                      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                        {devotee.name || devotee.full_name || 'N/A'}
                      </Typography>
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
                      {devotee.address ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <LocationOnIcon fontSize="small" color="action" />
                          {devotee.address}
                        </Box>
                      ) : (
                        'N/A'
                      )}
                    </TableCell>
                    <TableCell align="right">{devotee.donation_count || 0}</TableCell>
                    <TableCell align="right">
                      {formatCurrency(devotee.total_donated || 0)}
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
              Devotees will appear here once donations are recorded.
            </Typography>
          </Box>
        )}
      </Paper>
    </Layout>
  );
}

export default Devotees;
