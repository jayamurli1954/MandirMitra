import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import InventoryIcon from '@mui/icons-material/Inventory';
import StoreIcon from '@mui/icons-material/Store';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import ExitToAppIcon from '@mui/icons-material/ExitToApp';
import AssessmentIcon from '@mui/icons-material/Assessment';
import Layout from '../components/Layout';
import { useNavigate } from 'react-router-dom';

function Inventory() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({
    totalItems: 0,
    totalStores: 0,
    lowStockItems: 0,
    totalValue: 0
  });

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      // TODO: Add stats API endpoint
      // For now, use placeholder
      setStats({
        totalItems: 0,
        totalStores: 0,
        lowStockItems: 0,
        totalValue: 0
      });
    } catch (err) {
      console.error('Error fetching stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const menuCards = [
    {
      title: 'Item Master',
      description: 'Manage inventory items',
      icon: <InventoryIcon sx={{ fontSize: 48 }} />,
      color: '#4CAF50',
      path: '/inventory/items'
    },
    {
      title: 'Store Master',
      description: 'Manage storage locations',
      icon: <StoreIcon sx={{ fontSize: 48 }} />,
      color: '#2196F3',
      path: '/inventory/stores'
    },
    {
      title: 'Purchase Entry',
      description: 'Record inventory purchases',
      icon: <ShoppingCartIcon sx={{ fontSize: 48 }} />,
      color: '#FF9800',
      path: '/inventory/purchase'
    },
    {
      title: 'Issue Entry',
      description: 'Record inventory consumption',
      icon: <ExitToAppIcon sx={{ fontSize: 48 }} />,
      color: '#9C27B0',
      path: '/inventory/issue'
    },
    {
      title: 'Stock Report',
      description: 'View current stock balances',
      icon: <AssessmentIcon sx={{ fontSize: 48 }} />,
      color: '#F44336',
      path: '/inventory/stock-report'
    }
  ];

  return (
    <Layout>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3, fontWeight: 'bold' }}>
        Inventory Management
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Stats Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ boxShadow: 2, borderLeft: '4px solid #4CAF50' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {stats.totalItems}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Items
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ boxShadow: 2, borderLeft: '4px solid #2196F3' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {stats.totalStores}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Stores
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ boxShadow: 2, borderLeft: '4px solid #FF9800' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#FF9800' }}>
                    {stats.lowStockItems}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Low Stock Items
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ boxShadow: 2, borderLeft: '4px solid #9C27B0' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    ₹{new Intl.NumberFormat('en-IN').format(stats.totalValue)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Inventory Value
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Menu Cards */}
          <Grid container spacing={3}>
            {menuCards.map((card, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card
                  sx={{
                    boxShadow: 3,
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6
                    }
                  }}
                  onClick={() => navigate(card.path)}
                >
                  <CardContent sx={{ textAlign: 'center', p: 3 }}>
                    <Box sx={{ color: card.color, mb: 2 }}>
                      {card.icon}
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {card.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {card.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}
    </Layout>
  );
}

export default Inventory;


