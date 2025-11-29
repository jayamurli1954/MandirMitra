import React from 'react';
import { Box, Container, Typography, Grid, Card, CardContent, CardActions, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import InventoryIcon from '@mui/icons-material/Inventory';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import ConstructionIcon from '@mui/icons-material/Construction';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AssessmentIcon from '@mui/icons-material/Assessment';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import SettingsIcon from '@mui/icons-material/Settings';

const AssetManagement = () => {
  const navigate = useNavigate();

  const modules = [
    {
      title: 'Asset Master',
      description: 'Manage asset categories and asset master data',
      icon: <InventoryIcon sx={{ fontSize: 48, color: '#1976d2' }} />,
      path: '/assets/master',
      color: '#1976d2'
    },
    {
      title: 'Asset Purchase',
      description: 'Record new asset purchases',
      icon: <ShoppingCartIcon sx={{ fontSize: 48, color: '#2e7d32' }} />,
      path: '/assets/purchase',
      color: '#2e7d32'
    },
    {
      title: 'Capital Work in Progress',
      description: 'Track construction and installation projects',
      icon: <ConstructionIcon sx={{ fontSize: 48, color: '#ed6c02' }} />,
      path: '/assets/cwip',
      color: '#ed6c02'
    },
    {
      title: 'Depreciation',
      description: 'Calculate and post depreciation',
      icon: <TrendingDownIcon sx={{ fontSize: 48, color: '#d32f2f' }} />,
      path: '/assets/depreciation',
      color: '#d32f2f'
    },
    {
      title: 'Asset Reports',
      description: 'View asset register, depreciation schedules, and more',
      icon: <AssessmentIcon sx={{ fontSize: 48, color: '#9c27b0' }} />,
      path: '/assets/reports',
      color: '#9c27b0'
    },
    {
      title: 'Revaluation & Disposal',
      description: 'Revalue assets and record disposals',
      icon: <AccountBalanceIcon sx={{ fontSize: 48, color: '#0288d1' }} />,
      path: '/assets/revaluation',
      color: '#0288d1'
    },
    {
      title: 'Advanced Features',
      description: 'Asset transfers, verification, insurance, and documents',
      icon: <SettingsIcon sx={{ fontSize: 48, color: '#7b1fa2' }} />,
      path: '/assets/advanced',
      color: '#7b1fa2'
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 'bold', color: '#1976d2' }}>
        Asset Management
      </Typography>

      <Grid container spacing={3}>
        {modules.map((module, index) => (
          <Grid item xs={12} sm={6} md={4} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center', pt: 3 }}>
                <Box sx={{ mb: 2 }}>
                  {module.icon}
                </Box>
                <Typography variant="h6" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
                  {module.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {module.description}
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => navigate(module.path)}
                  sx={{ backgroundColor: module.color, '&:hover': { backgroundColor: module.color, opacity: 0.9 } }}
                >
                  Open
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default AssetManagement;


