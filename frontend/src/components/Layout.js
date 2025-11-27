import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Collapse,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import AssessmentIcon from '@mui/icons-material/Assessment';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TempleHinduIcon from '@mui/icons-material/TempleHindu';
import LogoutIcon from '@mui/icons-material/Logout';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import ReceiptIcon from '@mui/icons-material/Receipt';
import PaymentIcon from '@mui/icons-material/Payment';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import SummarizeIcon from '@mui/icons-material/Summarize';
import MoneyOffIcon from '@mui/icons-material/MoneyOff';
import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';
import InventoryIcon from '@mui/icons-material/Inventory';
import BusinessIcon from '@mui/icons-material/Business';
import GavelIcon from '@mui/icons-material/Gavel';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import Watermark from './Watermark';

const drawerWidth = 260;

// Base menu items (always visible)
const baseMenuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard', module: null }, // Always visible
  { text: 'Donations', icon: <AccountBalanceIcon />, path: '/donations', module: 'module_donations_enabled' },
  { text: 'Sevas', icon: <TempleHinduIcon />, path: '/sevas', module: 'module_sevas_enabled' },
  { text: 'Devotees', icon: <PeopleIcon />, path: '/devotees', module: null }, // Always visible
  { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory', module: 'module_inventory_enabled' },
  { text: 'Asset Management', icon: <BusinessIcon />, path: '/assets', module: 'module_assets_enabled' },
  { text: 'Tender Management', icon: <GavelIcon />, path: '/tenders', module: 'module_tender_enabled' },
  { text: 'HR & Payroll', icon: <PeopleAltIcon />, path: '/hr', module: 'module_hr_enabled' },
  { text: 'Reports', icon: <AssessmentIcon />, path: '/reports', module: 'module_reports_enabled' },
  { text: 'Panchang', icon: <CalendarTodayIcon />, path: '/panchang', module: 'module_panchang_enabled' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings', module: null }, // Always visible
];

const accountingMenuItems = [
  { text: 'Chart of Accounts', icon: <AccountTreeIcon />, path: '/accounting/chart-of-accounts' },
  { text: 'Quick Expense', icon: <MoneyOffIcon />, path: '/accounting/quick-expense' },
  { text: 'Journal Entries', icon: <ReceiptIcon />, path: '/accounting/journal-entries' },
  { text: 'UPI Payments', icon: <PaymentIcon />, path: '/accounting/upi-payments' },
  { text: 'Accounting Reports', icon: <SummarizeIcon />, path: '/accounting/reports' },
];

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [accountingOpen, setAccountingOpen] = useState(true); // Default to open
  const [showVideoFallback, setShowVideoFallback] = useState(false);
  const [moduleConfig, setModuleConfig] = useState({
    module_donations_enabled: true,
    module_sevas_enabled: true,
    module_inventory_enabled: true,
    module_assets_enabled: true,
    module_accounting_enabled: true,
    module_tender_enabled: true, // Enabled by default for demo/showcase
    module_hr_enabled: true, // HR & Salary Management
    module_panchang_enabled: true,
    module_reports_enabled: true,
    module_token_seva_enabled: true,
  });
  const navigate = useNavigate();
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  // Fetch module configuration on mount
  useEffect(() => {
    fetchModuleConfig();
  }, []);

  const fetchModuleConfig = async () => {
    try {
      const response = await axios.get('/api/v1/temples/modules/config', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setModuleConfig(response.data);
    } catch (err) {
      console.error('Failed to fetch module configuration:', err);
      // Use defaults if API fails (for demo/showcase)
    }
  };

  // Filter menu items based on module configuration
  const menuItems = baseMenuItems.filter(item => {
    if (item.module === null) return true; // Always show items without module requirement
    return moduleConfig[item.module] !== false; // Show if enabled or not set (default true)
  });

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const drawer = (
    <Box>
      <Box sx={{ p: 2, textAlign: 'center', bgcolor: '#FF9933', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1.5 }}>
        {!showVideoFallback ? (
          <video
            autoPlay
            loop
            muted
            playsInline
            onError={() => {
              console.error('Video logo load error - showing fallback');
              setShowVideoFallback(true);
            }}
            onLoadStart={() => console.log('Video logo loading...')}
            onLoadedData={() => console.log('Video logo loaded successfully')}
            style={{
              width: '60px',
              height: '60px',
              marginRight: '10px',
              objectFit: 'contain'
            }}
          >
            <source src="/mandirsync-logo.mp4" type="video/mp4" />
          </video>
        ) : (
          <Box
            component="img"
            src="/temple-gopuram.svg"
            alt="Temple Gopuram"
            sx={{
              height: 32,
              width: 32,
              filter: 'brightness(0) invert(1)', // Makes it white
            }}
          />
        )}
        <Typography 
          variant="h6" 
          sx={{ 
            fontWeight: 'bold', 
            color: 'white',
          }}
        >
          MandirSync
        </Typography>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                setMobileOpen(false);
              }}
              sx={{
                '&.Mui-selected': {
                  bgcolor: '#FFF3E0',
                  borderLeft: '4px solid #FF9933',
                  '&:hover': {
                    bgcolor: '#FFF3E0',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? '#FF9933' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={() => setAccountingOpen(!accountingOpen)}>
            <ListItemIcon>
              <AccountBalanceWalletIcon />
            </ListItemIcon>
            <ListItemText primary="Accounting" />
            {accountingOpen ? <ExpandLess /> : <ExpandMore />}
          </ListItemButton>
        </ListItem>
        <Collapse in={accountingOpen} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {accountingMenuItems.map((item) => (
              <ListItem key={item.text} disablePadding>
                <ListItemButton
                  selected={location.pathname === item.path}
                  onClick={() => {
                    navigate(item.path);
                    setMobileOpen(false);
                  }}
                  sx={{
                    pl: 4,
                    '&.Mui-selected': {
                      bgcolor: '#FFF3E0',
                      borderLeft: '4px solid #FF9933',
                      '&:hover': {
                        bgcolor: '#FFF3E0',
                      },
                    },
                  }}
                >
                  <ListItemIcon sx={{ color: location.pathname === item.path ? '#FF9933' : 'inherit' }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Collapse>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          bgcolor: '#FF9933',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            Temple Management System
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" sx={{ display: { xs: 'none', sm: 'block' } }}>
              {user.name || 'User'}
            </Typography>
            <IconButton onClick={handleMenuOpen} size="small">
              <Avatar sx={{ width: 32, height: 32, bgcolor: '#138808' }}>
                {user.name?.[0]?.toUpperCase() || 'U'}
              </Avatar>
            </IconButton>
          </Box>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          bgcolor: '#f5f5f5',
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        {children}
        <Watermark />
      </Box>
    </Box>
  );
}

export default Layout;

