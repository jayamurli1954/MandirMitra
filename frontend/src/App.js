import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { NotificationProvider } from './contexts/NotificationContext';
import { LoadingProvider } from './contexts/LoadingContext';
import { CurrentUserProvider } from './contexts/CurrentUserContext';
import ProtectedRoute from './components/ProtectedRoute';

const Login = lazy(() => import('./pages/Login'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
const ResetPassword = lazy(() => import('./pages/ResetPassword'));
const BrandIntro = lazy(() => import('./pages/BrandIntro'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Donations = lazy(() => import('./pages/Donations'));
const Devotees = lazy(() => import('./pages/Devotees'));
const Reports = lazy(() => import('./pages/Reports'));
const Panchang = lazy(() => import('./pages/Panchang'));
const PanchangSettings = lazy(() => import('./pages/PanchangSettings'));
const Sevas = lazy(() => import('./pages/Sevas'));
const SevaManagement = lazy(() => import('./pages/SevaManagement'));
const Settings = lazy(() => import('./pages/Settings'));
const SetupWizard = lazy(() => import('./pages/SetupWizard'));
const Profile = lazy(() => import('./pages/Profile'));
const TempleDirectory = lazy(() => import('./pages/TempleDirectory'));
const CategoryWiseDonationReport = lazy(() => import('./pages/CategoryWiseDonationReport'));
const DetailedDonationReport = lazy(() => import('./pages/DetailedDonationReport'));
const DetailedSevaReport = lazy(() => import('./pages/DetailedSevaReport'));
const SevaSchedule = lazy(() => import('./pages/SevaSchedule'));
const SevaRescheduleApproval = lazy(() => import('./pages/SevaRescheduleApproval'));
const Inventory = lazy(() => import('./pages/Inventory'));
const Assets = lazy(() => import('./pages/Assets'));
const HR = lazy(() => import('./pages/HR'));
const Hundi = lazy(() => import('./pages/Hundi'));
const ChartOfAccounts = lazy(() => import('./pages/accounting/ChartOfAccounts'));
const QuickExpense = lazy(() => import('./pages/accounting/QuickExpense'));
const JournalEntries = lazy(() => import('./pages/accounting/JournalEntries'));
const UpiPayments = lazy(() => import('./pages/accounting/UpiPayments'));
const BankReconciliation = lazy(() => import('./pages/accounting/BankReconciliation'));
const FinancialClosing = lazy(() => import('./pages/accounting/FinancialClosing'));
const AccountingReports = lazy(() => import('./pages/accounting/AccountingReports'));
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
          <CurrentUserProvider>
            <Router>
              <Suspense fallback={<div style={{ padding: 16 }}>Loading...</div>}>
                <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route
                path="/brand-intro"
                element={
                  <ProtectedRoute>
                    <BrandIntro />
                  </ProtectedRoute>
                }
              />
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
                path="/hundi"
                element={
                  <ProtectedRoute>
                    <Hundi />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/inventory"
                element={
                  <ProtectedRoute>
                    <Inventory />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/assets"
                element={
                  <ProtectedRoute>
                    <Assets />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/hr"
                element={
                  <ProtectedRoute>
                    <HR />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/setup-wizard"
                element={
                  <ProtectedRoute>
                    <SetupWizard />
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
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />

              <Route
                path="/platform/temples"
                element={
                  <ProtectedRoute>
                    <TempleDirectory />
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
                path="/accounting/bank-reconciliation"
                element={
                  <ProtectedRoute>
                    <BankReconciliation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/accounting/financial-closing"
                element={
                  <ProtectedRoute>
                    <FinancialClosing />
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
              </Suspense>
            </Router>
          </CurrentUserProvider>
        </LoadingProvider>
      </NotificationProvider>
    </ThemeProvider>
  );
}

export default App;






