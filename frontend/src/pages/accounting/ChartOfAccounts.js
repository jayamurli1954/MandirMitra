import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Collapse,
  Alert,
} from '@mui/material';
import Layout from '../../components/Layout';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

function AccountRow({ account, level = 0 }) {
  const [open, setOpen] = useState(level === 0);

  const getAccountTypeColor = (type) => {
    switch (type) {
      case 'ASSET':
        return 'success';
      case 'LIABILITY':
        return 'error';
      case 'INCOME':
        return 'primary';
      case 'EXPENSE':
        return 'warning';
      case 'EQUITY':
        return 'info';
      default:
        return 'default';
    }
  };

  const getAccountTypeIcon = (type) => {
    switch (type) {
      case 'ASSET':
        return <AccountBalanceIcon fontSize="small" />;
      case 'LIABILITY':
        return <TrendingDownIcon fontSize="small" />;
      case 'INCOME':
        return <TrendingUpIcon fontSize="small" />;
      case 'EXPENSE':
        return <TrendingDownIcon fontSize="small" />;
      case 'EQUITY':
        return <AccountBalanceWalletIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const hasSubAccounts = account.sub_accounts && account.sub_accounts.length > 0;

  return (
    <>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' }, bgcolor: level === 0 ? '#f5f5f5' : 'inherit' }}>
        <TableCell>
          {hasSubAccounts ? (
            <IconButton size="small" onClick={() => setOpen(!open)}>
              {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
            </IconButton>
          ) : (
            <Box sx={{ width: 40 }} />
          )}
        </TableCell>
        <TableCell>
          <Box sx={{ pl: level * 3 }}>{account.account_code}</Box>
        </TableCell>
        <TableCell>
          <Box sx={{ pl: level * 3, fontWeight: level === 0 ? 'bold' : 'normal' }}>
            {account.account_name}
          </Box>
        </TableCell>
        <TableCell>
          <Chip
            icon={getAccountTypeIcon(account.account_type)}
            label={account.account_type}
            size="small"
            color={getAccountTypeColor(account.account_type)}
          />
        </TableCell>
        <TableCell align="right">
          {account.is_system_account && (
            <Chip label="System" size="small" variant="outlined" />
          )}
        </TableCell>
        <TableCell>
          <Chip
            label={account.is_active ? 'Active' : 'Inactive'}
            size="small"
            color={account.is_active ? 'success' : 'default'}
          />
        </TableCell>
      </TableRow>
      {hasSubAccounts && (
        <TableRow>
          <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
            <Collapse in={open} timeout="auto" unmountOnExit>
              <Table size="small">
                <TableBody>
                  {account.sub_accounts.map((subAccount) => (
                    <AccountRow key={subAccount.id} account={subAccount} level={level + 1} />
                  ))}
                </TableBody>
              </Table>
            </Collapse>
          </TableCell>
        </TableRow>
      )}
    </>
  );
}

function ChartOfAccounts() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    ASSET: 0,
    LIABILITY: 0,
    INCOME: 0,
    EXPENSE: 0,
    EQUITY: 0,
  });

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/accounts/hierarchy`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();
      setAccounts(data);

      // Calculate stats
      const calculateStats = (accs) => {
        const newStats = { ASSET: 0, LIABILITY: 0, INCOME: 0, EXPENSE: 0, EQUITY: 0 };
        const countAccounts = (accounts) => {
          accounts.forEach((acc) => {
            newStats[acc.account_type]++;
            if (acc.sub_accounts && acc.sub_accounts.length > 0) {
              countAccounts(acc.sub_accounts);
            }
          });
        };
        countAccounts(accs);
        return newStats;
      };

      setStats(calculateStats(data));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching accounts:', error);
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AccountTreeIcon sx={{ fontSize: 40, mr: 2, color: '#FF9933' }} />
          <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
            Chart of Accounts
          </Typography>
        </Box>

        {/* Stats */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Asset Accounts</Typography>
            <Typography variant="h4" color="success.main">{stats.ASSET}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Liability Accounts</Typography>
            <Typography variant="h4" color="error.main">{stats.LIABILITY}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Income Accounts</Typography>
            <Typography variant="h4" color="primary.main">{stats.INCOME}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Expense Accounts</Typography>
            <Typography variant="h4" color="warning.main">{stats.EXPENSE}</Typography>
          </Paper>
          <Paper sx={{ p: 2, flex: 1, minWidth: 150 }}>
            <Typography variant="body2" color="text.secondary">Equity Accounts</Typography>
            <Typography variant="h4" color="info.main">{stats.EQUITY}</Typography>
          </Paper>
        </Box>

        <Alert severity="info" sx={{ mb: 3 }}>
          This is your complete chart of accounts hierarchy. Click the arrow icons to expand/collapse account groups.
        </Alert>

        {/* Accounts Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: '#FF9933' }}>
                  <TableCell sx={{ color: 'white', width: 50 }}></TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Code</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Account Name</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Type</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="right">System</TableCell>
                  <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography>Loading accounts...</Typography>
                    </TableCell>
                  </TableRow>
                ) : accounts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography color="text.secondary">No accounts found</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  accounts.map((account) => <AccountRow key={account.id} account={account} />)
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Box>
    </Layout>
  );
}

export default ChartOfAccounts;
