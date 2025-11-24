import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { NotificationProvider } from './contexts/NotificationContext';
import { LoadingProvider } from './contexts/LoadingContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Donations from './pages/Donations';
import Devotees from './pages/Devotees';
import Reports from './pages/Reports';
import Panchang from './pages/Panchang';
import PanchangSettings from './pages/PanchangSettings';
import Sevas from './pages/Sevas';
import SevaManagement from './pages/SevaManagement';
import Settings from './pages/Settings';
import CategoryWiseDonationReport from './pages/CategoryWiseDonationReport';
import DetailedDonationReport from './pages/DetailedDonationReport';
import DetailedSevaReport from './pages/DetailedSevaReport';
import SevaSchedule from './pages/SevaSchedule';
import SevaRescheduleApproval from './pages/SevaRescheduleApproval';
import ChartOfAccounts from './pages/accounting/ChartOfAccounts';
import QuickExpense from './pages/accounting/QuickExpense';
import JournalEntries from './pages/accounting/JournalEntries';
import UpiPayments from './pages/accounting/UpiPayments';
import AccountingReports from './pages/accounting/AccountingReports';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF9933', // Saffron color
    },
    secondary: {
      main: '#138808', // Green color
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <NotificationProvider>
        <LoadingProvider>
          <Router>
            <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/donations"
            element={
              <ProtectedRoute>
                <Donations />
              </ProtectedRoute>
            }
          />
          <Route
            path="/devotees"
            element={
              <ProtectedRoute>
                <Devotees />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports/donations/category-wise"
            element={
              <ProtectedRoute>
                <CategoryWiseDonationReport />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports/donations/detailed"
            element={
              <ProtectedRoute>
                <DetailedDonationReport />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports/sevas/detailed"
            element={
              <ProtectedRoute>
                <DetailedSevaReport />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports/sevas/schedule"
            element={
              <ProtectedRoute>
                <SevaSchedule />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sevas/reschedule-approval"
            element={
              <ProtectedRoute>
                <SevaRescheduleApproval />
              </ProtectedRoute>
            }
          />
          <Route
            path="/panchang"
            element={
              <ProtectedRoute>
                <Panchang />
              </ProtectedRoute>
            }
          />
          <Route
            path="/panchang/settings"
            element={
              <ProtectedRoute>
                <PanchangSettings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sevas"
            element={
              <ProtectedRoute>
                <Sevas />
              </ProtectedRoute>
            }
          />
          <Route
            path="/sevas/manage"
            element={
              <ProtectedRoute>
                <SevaManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accounting/chart-of-accounts"
            element={
              <ProtectedRoute>
                <ChartOfAccounts />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accounting/quick-expense"
            element={
              <ProtectedRoute>
                <QuickExpense />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accounting/journal-entries"
            element={
              <ProtectedRoute>
                <JournalEntries />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accounting/upi-payments"
            element={
              <ProtectedRoute>
                <UpiPayments />
              </ProtectedRoute>
            }
          />
          <Route
            path="/accounting/reports"
            element={
              <ProtectedRoute>
                <AccountingReports />
              </ProtectedRoute>
            }
          />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Router>
        </LoadingProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
}

export default App;

