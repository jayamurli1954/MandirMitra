import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
import LockIcon from '@mui/icons-material/Lock';
import InventoryIcon from '@mui/icons-material/Inventory';
import EngineeringIcon from '@mui/icons-material/Engineering';
import BadgeIcon from '@mui/icons-material/Badge';
import SavingsIcon from '@mui/icons-material/Savings';
import AssignmentIcon from '@mui/icons-material/Assignment';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';

const drawerWidth = 260;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard', module: 'always' },
  { text: 'Donations', icon: <AccountBalanceIcon />, path: '/donations', module: 'module_donations_enabled' },
  { text: 'Devotees', icon: <PeopleIcon />, path: '/devotees', module: 'always' },
  { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory', module: 'module_inventory_enabled' },
  { text: 'Temple Assets', icon: <EngineeringIcon />, path: '/assets', module: 'module_assets_enabled' },
  { text: 'HR & Salary', icon: <BadgeIcon />, path: '/hr', module: 'module_hr_enabled' },
  { text: 'Hundi', icon: <SavingsIcon />, path: '/hundi', module: 'module_hundi_enabled' },
  { text: 'Reports', icon: <AssessmentIcon />, path: '/reports', module: 'module_reports_enabled' },
  { text: 'Panchang', icon: <CalendarTodayIcon />, path: '/panchang', module: 'module_panchang_enabled' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings', module: 'always' },
];

const sevaMenuItems = [
  { text: 'Book Sevas', icon: <TempleHinduIcon />, path: '/sevas' },
  { text: 'Seva Bookings / Reschedule', icon: <AssignmentIcon />, path: '/reports/sevas/detailed' },
  { text: 'Seva Management', icon: <AssignmentIcon />, path: '/sevas/manage' },
  { text: 'Reschedule Approval', icon: <AssignmentTurnedInIcon />, path: '/sevas/reschedule-approval' },
];

const accountingMenuItems = [
  { text: 'Chart of Accounts', icon: <AccountTreeIcon />, path: '/accounting/chart-of-accounts' },
  { text: 'Quick Expense', icon: <MoneyOffIcon />, path: '/accounting/quick-expense' },
  { text: 'Journal Entries', icon: <ReceiptIcon />, path: '/accounting/journal-entries' },
  { text: 'Bank Reconciliation', icon: <AccountBalanceIcon />, path: '/accounting/bank-reconciliation' },
  { text: 'Financial Closing', icon: <LockIcon />, path: '/accounting/financial-closing' },
  { text: 'UPI Payments', icon: <PaymentIcon />, path: '/accounting/upi-payments' },
  { text: 'Accounting Reports', icon: <SummarizeIcon />, path: '/accounting/reports' },
];

const DEFAULT_MODULE_CONFIG = {
  module_donations_enabled: true,
  module_sevas_enabled: true,
  module_inventory_enabled: false,
  module_assets_enabled: false,
  module_hr_enabled: false,
  module_hundi_enabled: false,
  module_accounting_enabled: true,
  module_reports_enabled: true,
  module_panchang_enabled: true,
};

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [accountingOpen, setAccountingOpen] = useState(true);
  const [sevasOpen, setSevasOpen] = useState(true);
  const [moduleConfig, setModuleConfig] = useState(DEFAULT_MODULE_CONFIG);
  const navigate = useNavigate();
  const location = useLocation();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const canApproveReschedule =
    ['admin', 'temple_manager'].includes(user.role) || Boolean(user.is_superuser);
  const visibleSevaMenuItems = sevaMenuItems.filter(
    (item) => item.path !== '/sevas/reschedule-approval' || canApproveReschedule
  );

  React.useEffect(() => {
    const fetchTempleInfo = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/v1/temples/`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          // The API returns a list, take the first one
          const temple = Array.isArray(data) ? data[0] : data;
          setModuleConfig({ ...DEFAULT_MODULE_CONFIG, ...(temple || {}) });
        }
      } catch (err) {
        console.error('Failed to fetch temple info', err);
      }
    };
    fetchTempleInfo();
  }, []);

  React.useEffect(() => {
    const handleModuleConfigUpdated = (event) => {
      if (event?.detail && typeof event.detail === 'object') {
        setModuleConfig((prev) => ({ ...prev, ...event.detail }));
      }
    };

    window.addEventListener('module-config-updated', handleModuleConfigUpdated);
    return () => window.removeEventListener('module-config-updated', handleModuleConfigUpdated);
  }, []);

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
      <Box
        sx={{
          p: 1.5,
          textAlign: 'center',
          bgcolor: '#FF9933',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Box
          component="img"
          src="/branding/mandirmitra_logo1.jpg"
          alt="MandirMitra Logo"
          sx={{
            height: 58,
            width: '100%',
            maxWidth: 220,
            objectFit: 'contain',
          }}
        />
      </Box>
      <Divider />
      <List>
        {/* Dashboard - First Item */}
        {menuItems
          .filter(item => item.text === 'Dashboard')
          .map((item) => (
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

        {/* Sevas - Second Item Block */}
        {moduleConfig.module_sevas_enabled && (
          <>
            <ListItem disablePadding>
              <ListItemButton onClick={() => setSevasOpen(!sevasOpen)}>
                <ListItemIcon>
                  <TempleHinduIcon />
                </ListItemIcon>
                <ListItemText primary="Sevas" />
                {sevasOpen ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
            </ListItem>
            <Collapse in={sevasOpen} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {visibleSevaMenuItems.map((item) => (
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
            <Divider />
          </>
        )}

        {/* Other Menu Items starting with Donations */}
        {menuItems
          .filter(item => item.text !== 'Dashboard')
          .filter(item => item.module === 'always' || moduleConfig[item.module])
          .map((item) => (
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
      {moduleConfig.module_accounting_enabled && (
        <>
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
          <Divider />
        </>
      )}
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
        <Toolbar sx={{ position: 'relative' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Box
            sx={{
              position: 'absolute',
              left: '50%',
              transform: 'translateX(-50%)',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              px: { xs: 1, sm: 1.2 },
              py: 0.7,
              borderRadius: 1.5,
              bgcolor: 'rgba(255,255,255,0.16)',
              border: '1px solid rgba(255,255,255,0.25)',
              minWidth: 0,
              maxWidth: { xs: 'calc(100% - 180px)', sm: 'calc(100% - 260px)' },
            }}
          >
            {moduleConfig?.logo_url ? (
              <Box
                component="img"
                src={moduleConfig.logo_url}
                alt="Temple Logo"
                sx={{
                  height: 30,
                  width: 30,
                  borderRadius: '50%',
                  bgcolor: 'white',
                  p: 0.25,
                  flexShrink: 0,
                }}
              />
            ) : (
              <TempleHinduIcon sx={{ fontSize: 22, color: '#fff', flexShrink: 0 }} />
            )}

            <Box sx={{ minWidth: 0 }}>
              <Typography
                variant="body1"
                sx={{
                  fontWeight: 700,
                  color: '#fff',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  lineHeight: 1.1,
                  maxWidth: { xs: '160px', sm: '340px', md: '520px' },
                }}
              >
                {moduleConfig?.name || 'Sri Vara Siddi Vinayak Temple'}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  color: 'rgba(255,255,255,0.95)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  maxWidth: { xs: '160px', sm: '340px', md: '520px' },
                }}
              >
                Temple Management &amp; Accounting System
              </Typography>
            </Box>
          </Box>
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
      </Box>
    </Box>
  );
}

export default Layout;

