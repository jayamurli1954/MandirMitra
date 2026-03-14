import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { fetchWithApiFallback } from '../utils/apiBaseUrl';
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
  FormControl,
  MenuItem,
  Select,
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
import { useCurrentUser } from '../contexts/CurrentUserContext';
import { clearAuthSession, getAccessToken, hasAccessToken } from '../utils/authStorage';

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
  { text: 'Temples / Trusts', icon: <TempleHinduIcon />, path: '/platform/temples', superAdminOnly: true },
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
const ACTIVE_TEMPLE_STORAGE_KEY = 'active_temple_id_v1';

const readActiveTempleId = () => {
  const raw = localStorage.getItem(ACTIVE_TEMPLE_STORAGE_KEY);
  if (!raw) {
    return null;
  }
  const parsed = Number.parseInt(raw, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
};

const writeActiveTempleId = (templeId) => {
  if (!templeId) {
    localStorage.removeItem(ACTIVE_TEMPLE_STORAGE_KEY);
    return;
  }
  localStorage.setItem(ACTIVE_TEMPLE_STORAGE_KEY, String(templeId));
};

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
  const { user, clearUser, loading: currentUserLoading } = useCurrentUser();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [accountingOpen, setAccountingOpen] = useState(true);
  const [sevasOpen, setSevasOpen] = useState(true);
  const [moduleConfig, setModuleConfig] = useState(DEFAULT_MODULE_CONFIG);
  const navigate = useNavigate();
  const location = useLocation();
  const [temples, setTemples] = useState([]);
  const [activeTempleId, setActiveTempleId] = useState(() => readActiveTempleId());
  const userInfo = user || {};

  const systemRole = userInfo.system_role || userInfo.role;
  const modulePermissions = userInfo.module_permissions || {};
  const actionPermissions = userInfo.action_permissions || {};
  const hasResolvedCurrentUser = Boolean(userInfo.id || userInfo.email || userInfo.role || userInfo.system_role || userInfo.is_superuser);
  const hasModuleAccess = (permissionKey) => {
    if ((currentUserLoading && hasAccessToken()) || (!hasResolvedCurrentUser && hasAccessToken())) {
      return false;
    }
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
    if ((currentUserLoading && hasAccessToken()) || (!hasResolvedCurrentUser && hasAccessToken())) {
      return false;
    }
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
    !currentUserLoading && (hasActionAccess('manage_seva_master') || ['admin', 'super_admin', 'temple_manager'].includes(systemRole) || Boolean(userInfo.is_superuser));
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
  const isPlatformSuperAdmin = Boolean(userInfo.is_superuser) || systemRole === 'super_admin';

  useEffect(() => {
    const fetchTempleInfo = async () => {
      const cachedModuleConfig = readLayoutCache(MODULE_CONFIG_CACHE_KEY);
      if (cachedModuleConfig && typeof cachedModuleConfig === 'object') {
        setModuleConfig({ ...DEFAULT_MODULE_CONFIG, ...cachedModuleConfig });
      }

      try {
        const token = getAccessToken();
        if (!token) {
          return;
        }

        const response = await fetchWithApiFallback('/api/v1/temples/', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }, { timeoutMs: 12000 });
        if (!response.ok) {
          return;
        }

        const data = await response.json();
        const templeList = Array.isArray(data) ? data : (data ? [data] : []);
        setTemples(templeList);
        if (!templeList.length) {
          return;
        }

        const preferredTemple = templeList.find((temple) => temple.id === activeTempleId) || templeList[0];
        if (preferredTemple?.id && preferredTemple.id !== activeTempleId) {
          writeActiveTempleId(preferredTemple.id);
          setActiveTempleId(preferredTemple.id);
        }

        const normalized = { ...DEFAULT_MODULE_CONFIG, ...(preferredTemple || {}) };
        setModuleConfig(normalized);
        writeLayoutCache(MODULE_CONFIG_CACHE_KEY, normalized);
      } catch (err) {
        console.error('Failed to fetch temple info', err);
      }
    };
    fetchTempleInfo();
  }, [activeTempleId]);

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
    const handleActiveTempleChanged = (event) => {
      const nextTempleId = Number.parseInt(String(event?.detail?.templeId || ''), 10);
      if (Number.isInteger(nextTempleId) && nextTempleId > 0) {
        writeActiveTempleId(nextTempleId);
        setActiveTempleId(nextTempleId);
      }
    };

    window.addEventListener('active-temple-changed', handleActiveTempleChanged);
    return () => window.removeEventListener('active-temple-changed', handleActiveTempleChanged);
  }, []);



  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  const handleLogout = () => {
    clearAuthSession();
    localStorage.removeItem(MODULE_CONFIG_CACHE_KEY);
    localStorage.removeItem(ACTIVE_TEMPLE_STORAGE_KEY);
    clearUser();
    window.dispatchEvent(new CustomEvent('auth-state-changed', { detail: { clear: true } }));
    navigate('/login');
  };

  const visibleMenuItems = menuItems.filter((item) => {
    if (item.superAdminOnly && !isPlatformSuperAdmin) {
      return false;
    }
    return isFeatureEnabled(item.moduleFlag) && hasModuleAccess(item.permissionKey);
  });
  const showSevaSection = isFeatureEnabled('module_sevas_enabled') && hasModuleAccess('sevas');
  const showAccountingSection = isFeatureEnabled('module_accounting_enabled') && hasModuleAccess('accounting');

  const handleActiveTempleChange = (event) => {
    const nextTempleId = Number.parseInt(String(event.target.value), 10);
    if (!Number.isInteger(nextTempleId) || nextTempleId <= 0) {
      return;
    }

    writeActiveTempleId(nextTempleId);
    setActiveTempleId(nextTempleId);
    window.dispatchEvent(new CustomEvent('active-temple-changed', {
      detail: { templeId: nextTempleId },
    }));
  };

  const showTempleSwitcher = temples.length > 1 && isPlatformSuperAdmin;
  const currentTempleLabel = moduleConfig?.name || moduleConfig?.trust_name || 'MandirMitra';

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
                {currentTempleLabel}
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
              {showTempleSwitcher && (
                <FormControl
                  variant="standard"
                  size="small"
                  sx={{
                    mt: 0.5,
                    minWidth: { xs: 180, sm: 240 },
                    '& .MuiInputBase-root': { color: '#fff', fontSize: 14, fontWeight: 600 },
                    '& .MuiSvgIcon-root': { color: '#fff' },
                    '& .MuiInput-underline:before': { borderBottomColor: 'rgba(255,255,255,0.55)' },
                    '& .MuiInput-underline:hover:not(.Mui-disabled):before': { borderBottomColor: '#fff' },
                    '& .MuiInput-underline:after': { borderBottomColor: '#fff' },
                  }}
                >
                  <Select
                    value={activeTempleId ? String(activeTempleId) : ''}
                    onChange={handleActiveTempleChange}
                    disableUnderline
                    displayEmpty
                  >
                    {temples.map((temple) => (
                      <MenuItem key={temple.id} value={String(temple.id)}>
                        {temple.name || temple.trust_name || `Temple ${temple.id}`}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}
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


