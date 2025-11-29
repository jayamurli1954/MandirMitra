import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { NotificationProvider } from './contexts/NotificationContext';
import { LoadingProvider } from './contexts/LoadingContext';
import Login from './pages/Login';
import Splash from './pages/Splash';
import Dashboard from './pages/Dashboard';
import Donations from './pages/Donations';
import Devotees from './pages/Devotees';
import Reports from './pages/Reports';
import Panchang from './pages/Panchang';
import PanchangSettings from './pages/PanchangSettings';
import Kundli from './pages/Kundli';
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
import Inventory from './pages/Inventory';
import ItemMaster from './pages/inventory/ItemMaster';
import StoreMaster from './pages/inventory/StoreMaster';
import PurchaseEntry from './pages/inventory/PurchaseEntry';
import IssueEntry from './pages/inventory/IssueEntry';
import StockReport from './pages/inventory/StockReport';
import StockAuditWastage from './pages/inventory/StockAuditWastage';
import AssetManagement from './pages/AssetManagement';
import AssetMaster from './pages/assets/AssetMaster';
import AssetPurchase from './pages/assets/AssetPurchase';
import CWIPManagement from './pages/assets/CWIPManagement';
import DepreciationPage from './pages/assets/DepreciationPage';
import AssetReportsPage from './pages/assets/AssetReportsPage';
import RevaluationDisposal from './pages/assets/RevaluationDisposal';
import AssetManagementAdvanced from './pages/assets/AssetManagementAdvanced';
import TenderManagement from './pages/tenders/TenderManagement';
import HRManagement from './pages/hr/HRManagement';
import HundiManagement from './pages/hundi/HundiManagement';
import BankReconciliation from './pages/accounting/BankReconciliation';
import FinancialClosing from './pages/accounting/FinancialClosing';
import BankAccounts from './pages/accounting/BankAccounts';
import TokenSeva from './pages/TokenSeva';
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
            path="/splash"
            element={
              <ProtectedRoute>
                <Splash />
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
          {/* Kundli route - Hidden from menu but accessible if users specifically request it */}
          <Route
            path="/kundli"
            element={
              <ProtectedRoute>
                <Kundli />
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
            path="/accounting/bank-accounts"
            element={
              <ProtectedRoute>
                <BankAccounts />
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
          <Route
            path="/inventory"
            element={
              <ProtectedRoute>
                <Inventory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory/items"
            element={
              <ProtectedRoute>
                <ItemMaster />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory/stores"
            element={
              <ProtectedRoute>
                <StoreMaster />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory/purchase"
            element={
              <ProtectedRoute>
                <PurchaseEntry />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory/issue"
            element={
              <ProtectedRoute>
                <IssueEntry />
              </ProtectedRoute>
            }
          />
          <Route
            path="/inventory/stock-report"
            element={
              <ProtectedRoute>
                <StockReport />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets"
            element={
              <ProtectedRoute>
                <AssetManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/master"
            element={
              <ProtectedRoute>
                <AssetMaster />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/purchase"
            element={
              <ProtectedRoute>
                <AssetPurchase />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/cwip"
            element={
              <ProtectedRoute>
                <CWIPManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/depreciation"
            element={
              <ProtectedRoute>
                <DepreciationPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/reports"
            element={
              <ProtectedRoute>
                <AssetReportsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/revaluation"
            element={
              <ProtectedRoute>
                <RevaluationDisposal />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assets/advanced"
            element={
              <ProtectedRoute>
                <AssetManagementAdvanced />
              </ProtectedRoute>
            }
          />
          <Route
            path="/tenders"
            element={
              <ProtectedRoute>
                <TenderManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/hr"
            element={
              <ProtectedRoute>
                <HRManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/hundi"
            element={
              <ProtectedRoute>
                <HundiManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/token-seva"
            element={
              <ProtectedRoute>
                <TokenSeva />
              </ProtectedRoute>
            }
          />
          <Route
            path="/bank-reconciliation"
            element={
              <ProtectedRoute>
                <BankReconciliation />
              </ProtectedRoute>
            }
          />
          <Route
            path="/financial-closing"
            element={
              <ProtectedRoute>
                <FinancialClosing />
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

