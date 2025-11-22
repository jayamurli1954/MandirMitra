import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Donations from './pages/Donations';
import Devotees from './pages/Devotees';
import Reports from './pages/Reports';
import Panchang from './pages/Panchang';
import Sevas from './pages/Sevas';
import SevaManagement from './pages/SevaManagement';
import Settings from './pages/Settings';
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
            path="/panchang"
            element={
              <ProtectedRoute>
                <Panchang />
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
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;

