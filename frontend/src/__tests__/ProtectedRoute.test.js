/**
 * Tests for ProtectedRoute component (src/components/ProtectedRoute.js)
 * Covers: redirect when unauthenticated, setup-wizard redirect behaviour, and exempt profile access
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';
import { fetchWithApiFallback } from '../utils/apiBaseUrl';

jest.mock('../utils/apiBaseUrl', () => ({
  fetchWithApiFallback: jest.fn(),
}));

const ProtectedPage = ({ label = 'Protected Content' }) => <div>{label}</div>;
const LoginPage = () => <div>Login Page</div>;
const SetupWizardPage = () => <div>First-Time Setup Wizard</div>;

const renderWithRoute = (initialEntry = '/dashboard', protectedPath = '/dashboard') => {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/setup-wizard" element={<SetupWizardPage />} />
        <Route
          path={protectedPath}
          element={
            <ProtectedRoute>
              <ProtectedPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>
  );
};

beforeEach(() => {
  localStorage.clear();
  fetchWithApiFallback.mockReset();
  fetchWithApiFallback.mockResolvedValue({
    ok: true,
    json: async () => ({
      force_setup: false,
      can_manage_setup: true,
    }),
  });
});

describe('ProtectedRoute', () => {
  it('redirects to /login when no token in localStorage', () => {
    renderWithRoute('/dashboard');
    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
    expect(screen.queryByText(/Protected Content/i)).not.toBeInTheDocument();
  });

  it('renders children when token exists in localStorage', async () => {
    localStorage.setItem('token', 'valid-jwt-token');
    renderWithRoute('/dashboard');
    await waitFor(() => expect(screen.getByText(/Protected Content/i)).toBeInTheDocument());
    expect(screen.queryByText(/Login Page/i)).not.toBeInTheDocument();
  });

  it('redirects to /login when token is empty string', () => {
    localStorage.setItem('token', '');
    renderWithRoute('/dashboard');
    expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
  });

  it('redirects non-exempt routes to the setup wizard when forced setup is required', async () => {
    localStorage.setItem('token', 'valid-jwt-token');
    fetchWithApiFallback.mockResolvedValue({
      ok: true,
      json: async () => ({
        force_setup: true,
        can_manage_setup: true,
      }),
    });

    renderWithRoute('/dashboard');

    await waitFor(() => expect(screen.getByText(/First-Time Setup Wizard/i)).toBeInTheDocument());
  });

  it('keeps the profile route accessible even when forced setup is required', async () => {
    localStorage.setItem('token', 'valid-jwt-token');
    fetchWithApiFallback.mockResolvedValue({
      ok: true,
      json: async () => ({
        force_setup: true,
        can_manage_setup: true,
      }),
    });

    renderWithRoute('/profile', '/profile');

    await waitFor(() => expect(screen.getByText(/Protected Content/i)).toBeInTheDocument());
    expect(screen.queryByText(/First-Time Setup Wizard/i)).not.toBeInTheDocument();
  });
});
