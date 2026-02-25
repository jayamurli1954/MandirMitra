/**
 * Tests for ProtectedRoute component (src/components/ProtectedRoute.js)
 * Covers: redirect when unauthenticated, renders children when authenticated
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import ProtectedRoute from '../components/ProtectedRoute';

const ProtectedPage = () => <div>Protected Content</div>;
const LoginPage = () => <div>Login Page</div>;

const renderWithRoute = (initialEntry = '/dashboard') => {
    return render(
        <MemoryRouter initialEntries={[initialEntry]}>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                    path="/dashboard"
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
});

describe('ProtectedRoute', () => {
    it('redirects to /login when no token in localStorage', () => {
        renderWithRoute('/dashboard');
        expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
        expect(screen.queryByText(/Protected Content/i)).not.toBeInTheDocument();
    });

    it('renders children when token exists in localStorage', () => {
        localStorage.setItem('token', 'valid-jwt-token');
        renderWithRoute('/dashboard');
        expect(screen.getByText(/Protected Content/i)).toBeInTheDocument();
        expect(screen.queryByText(/Login Page/i)).not.toBeInTheDocument();
    });

    it('redirects to /login when token is empty string', () => {
        localStorage.setItem('token', '');
        renderWithRoute('/dashboard');
        // Empty string is falsy, so should redirect
        expect(screen.getByText(/Login Page/i)).toBeInTheDocument();
    });
});
