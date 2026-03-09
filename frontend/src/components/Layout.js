import React, { useState, useEffect } from 'react';
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
  Button,
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
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard', permissionKey: 'dashboard' },
  { text: 'Donations', icon: <AccountBalanceIcon />, path: '/donations', moduleFlag: 'module_donations_enabled', permissionKey: 'donations' },
  { text: 'Devotees', icon: <PeopleIcon />, path: '/devotees', permissionKey: 'devotees' },
  { text: 'Inventory', icon: <InventoryIcon />, path: '/inventory', moduleFlag: 'module_inventory_enabled', permissionKey: 'inventory' },
  { text: 'Temple Assets', icon: <EngineeringIcon />, path: '/assets', moduleFlag: 'module_assets_enabled', permissionKey: 'assets' },
  { text: 'HR & Salary', icon: <BadgeIcon />, path: '/hr', moduleFlag: 'module_hr_enabled', permissionKey: 'hr' },
  { text: 'Hundi', icon: <SavingsIcon />, path: '/hundi', moduleFlag: 'module_hundi_enabled', permissionKey: 'hundi' },
  { text: 'Reports', icon: <AssessmentIcon />, path: '/reports', moduleFlag: 'module_reports_enabled', permissionKey: 'reports' },
  { text: 'Panchang', icon: <CalendarTodayIcon />, path: '/panchang', moduleFlag: 'module_panchang_enabled', permissionKey: 'panchang' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings', permissionKey: 'settings' },
];

const sevaMenuItems = [
  { text: 'Book Sevas', icon: <TempleHinduIcon />, path: '/sevas' },
  { text: 'Seva Bookings / Reschedule', icon: <AssignmentIcon />, path: '/reports/sevas/detailed' },
  { text: 'Seva Management', icon: <AssignmentIcon />, path: '/sevas/manage', requires: 'manage_seva_master' },
  { text: 'Reschedule Approval', icon: <AssignmentTurnedInIcon />, path: '/sevas/reschedule-approval', requires: 'approve_seva_reschedule' },
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

const LAYOUT_CACHE_TTL_MS = 2 * 60 * 1000;
const MODULE_CONFIG_CACHE_KEY = 'layout_module_config_cache_v1';
const USER_PROFILE_CACHE_KEY = 'layout_user_profile_cache_v1';

const readLayoutCache = (key) => {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== 'object') {
      localStorage.removeItem(key);
      return null;
    }

    if (typeof parsed.expiresAt !== 'number' || Date.now() > parsed.expiresAt) {
      localStorage.removeItem(key);
      return null;
    }

    return parsed.value ?? null;
  } catch (err) {
    localStorage.removeItem(key);
    return null;
  }
};

const writeLayoutCache = (key, value, ttlMs = LAYOUT_CACHE_TTL_MS) => {
  try {
    localStorage.setItem(
      key,
      JSON.stringify({
        value,
        expiresAt: Date.now() + ttlMs,
      })
    );
  } catch (err) {
    // Ignore storage write failures.
  }
};

function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [accountingOpen, setAccountingOpen] = useState(true);
  const [sevasOpen, setSevasOpen] = useState(true);
  const [moduleConfig, setModuleConfig] = useState(DEFAULT_MODULE_CONFIG);
  const navigate = useNavigate();
  const location = useLocation();
  const [userInfo, setUserInfo] = useState(() => {
    const cachedProfile = readLayoutCache(USER_PROFILE_CACHE_KEY);
    if (cachedProfile && typeof cachedProfile === 'object') {
      return cachedProfile;
    }
    return JSON.parse(localStorage.getItem('user') || '{}');
  });

  const systemRole = userInfo.system_role || userInfo.role;
  const modulePermissions = userInfo.module_permissions || {};
  const actionPermissions = userInfo.action_permissions || {};
  const hasModuleAccess = (permissionKey) => {
    if (userInfo.is_superuser) {
      return true;
    }
    if (!permissionKey) {
      return true;
    }
    if (Object.prototype.hasOwnProperty.call(modulePermissions, permissionKey)) {
      return Boolean(modulePermissions[permissionKey]);
    }
    return true;
  };
  const hasActionAccess = (permissionKey) => {
    if (userInfo.is_superuser) {
      return true;
    }
    if (!permissionKey) {
      return true;
    }
    if (Object.prototype.hasOwnProperty.call(actionPermissions, permissionKey)) {
      return Boolean(actionPermissions[permissionKey]);
    }
    return false;
  };
  const isFeatureEnabled = (moduleFlag) => {
    if (!moduleFlag) {
      return true;
    }
    return Boolean(moduleConfig[moduleFlag]);
  };

  const isSevaManager =
    hasActionAccess('manage_seva_master') || ['admin', 'super_admin', 'temple_manager'].includes(systemRole) || Boolean(userInfo.is_superuser);
  const canApproveReschedule = hasActionAccess('approve_seva_reschedule') || isSevaManager;

  const visibleSevaMenuItems = sevaMenuItems.filter((item) => {
    if (item.requires === 'manage_seva_master') {
      return isSevaManager;
    }
    if (item.requires === 'approve_seva_reschedule') {
      return canApproveReschedule;
    }
    return true;
  });

  const displayName =
    userInfo.full_name || userInfo.name || (userInfo.email ? userInfo.email.split('@')[0] : '') || 'Admin';

  useEffect(() => {
    const fetchTempleInfo = async () => {
      const cachedModuleConfig = readLayoutCache(MODULE_CONFIG_CACHE_KEY);
      if (cachedModuleConfig && typeof cachedModuleConfig === 'object') {
        setModuleConfig({ ...DEFAULT_MODULE_CONFIG, ...cachedModuleConfig });
        return;
      }

      try {
        const token = localStorage.getItem('token');
        if (!token) {
          return;
        }

        const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/v1/temples/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          const temple = Array.isArray(data) ? data[0] : data;
          const normalized = { ...DEFAULT_MODULE_CONFIG, ...(temple || {}) };
          setModuleConfig(normalized);
          writeLayoutCache(MODULE_CONFIG_CACHE_KEY, normalized);
        }
      } catch (err) {
        console.error('Failed to fetch temple info', err);
      }
    };
    fetchTempleInfo();
  }, []);

  useEffect(() => {
    const handleModuleConfigUpdated = (event) => {
      if (event?.detail && typeof event.detail === 'object') {
        setModuleConfig((prev) => {
          const merged = { ...prev, ...event.detail };
          writeLayoutCache(MODULE_CONFIG_CACHE_KEY, merged);
          return merged;
        });
      }
    };

    window.addEventListener('module-config-updated', handleModuleConfigUpdated);
    return () => window.removeEventListener('module-config-updated', handleModuleConfigUpdated);
  }, []);

  useEffect(() => {
    const handleProfileUpdated = (event) => {
      if (event?.detail && typeof event.detail === 'object') {
        const merged = {
          ...(JSON.parse(localStorage.getItem('user') || '{}')),
          ...event.detail,
        };
        setUserInfo(merged);
        localStorage.setItem('user', JSON.stringify(merged));
        writeLayoutCache(USER_PROFILE_CACHE_KEY, merged);
      }
    };

    const fetchCurrentUser = async () => {
      const cachedProfile = readLayoutCache(USER_PROFILE_CACHE_KEY);
      if (cachedProfile && (cachedProfile.id || cachedProfile.email)) {
        setUserInfo(cachedProfile);
        return;
      }

      try {
        const token = localStorage.getItem('token');
        if (!token) {
          return;
        }

        const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/api/v1/users/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          return;
        }

        const data = await response.json();
        const normalized = {
          ...(JSON.parse(localStorage.getItem('user') || '{}')),
          id: data.id,
          email: data.email,
          full_name: data.full_name,
          name: data.full_name || data.email,
          role: data.system_role || data.role,
          system_role: data.system_role || data.role,
          role_key: data.role_key,
          role_label: data.role_label,
          phone: data.phone || '',
          module_permissions: data.module_permissions || {},
          action_permissions: data.action_permissions || {},
          is_superuser: Boolean(data.is_superuser),
        };
        setUserInfo(normalized);
        localStorage.setItem('user', JSON.stringify(normalized));
        writeLayoutCache(USER_PROFILE_CACHE_KEY, normalized);
      } catch (err) {
        console.error('Failed to fetch current user profile', err);
      }
    };

    window.addEventListener('user-profile-updated', handleProfileUpdated);
    fetchCurrentUser();

    return () => window.removeEventListener('user-profile-updated', handleProfileUpdated);
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem(MODULE_CONFIG_CACHE_KEY);
    localStorage.removeItem(USER_PROFILE_CACHE_KEY);
    setUserInfo({});
    navigate('/login');
  };

  const visibleMenuItems = menuItems.filter((item) => isFeatureEnabled(item.moduleFlag) && hasModuleAccess(item.permissionKey));
  const showSevaSection = isFeatureEnabled('module_sevas_enabled') && hasModuleAccess('sevas');
  const showAccountingSection = isFeatureEnabled('module_accounting_enabled') && hasModuleAccess('accounting');

  const drawer = (
    <Box sx={{ height: '100%', overflowY: 'auto' }}>
      <Toolbar />
      <Divider />
      <List>
        {visibleMenuItems
          .filter((item) => item.text === 'Dashboard')
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
                    '&:hover': { bgcolor: '#FFF3E0' },
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

        {showSevaSection && (
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
                          '&:hover': { bgcolor: '#FFF3E0' },
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

        {visibleMenuItems
          .filter((item) => item.text !== 'Dashboard')
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
                    '&:hover': { bgcolor: '#FFF3E0' },
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
      {showAccountingSection && (
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
                          '&:hover': { bgcolor: '#FFF3E0' },
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
          width: '100%',
          ml: 0,
          bgcolor: '#FF9933',
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
      >
        <Toolbar sx={{ display: 'flex', alignItems: 'center', gap: 1, minHeight: { xs: 64, sm: 72 } }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              width: { sm: drawerWidth },
              minWidth: 0,
              pr: 1,
              flexShrink: 0,
            }}
          >
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 0.5, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Box
              component="img"
              src="/branding/mandirmitra_logo1.jpg"
              alt="MandirMitra Logo"
              sx={{
                height: { xs: 40, sm: 52 },
                width: '100%',
                maxWidth: { xs: 160, sm: 230 },
                objectFit: 'contain',
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1, minWidth: 0, pl: { xs: 0.2, sm: 1 } }}>
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
                }}
              >
                {moduleConfig?.name || moduleConfig?.trust_name || 'MandirMitra'}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: { xs: 'none', md: 'block' },
                  color: 'rgba(255,255,255,0.95)',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                Temple / Trust Management &amp; Accounting System
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.8, ml: 'auto' }}>
            <Button
              color="inherit"
              onClick={handleProfileClick}
              sx={{ textTransform: 'none', fontWeight: 700, minWidth: 0, px: { xs: 0.5, sm: 1.2 } }}
            >
              {displayName}
            </Button>
            <IconButton color="inherit" onClick={handleProfileClick} size="small" aria-label="profile">
              <Avatar sx={{ width: 32, height: 32, bgcolor: '#138808' }}>
                {displayName?.[0]?.toUpperCase() || 'U'}
              </Avatar>
            </IconButton>
            <Button
              color="inherit"
              startIcon={<LogoutIcon />}
              onClick={handleLogout}
              sx={{ textTransform: 'none', fontWeight: 700, px: { xs: 0.5, sm: 1.2 } }}
            >
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
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
