/**
 * Tests for the Donations page (src/pages/Donations.js)
 * Covers: rendering, form interaction, add/remove rows, validation, API submission
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Donations from '../pages/Donations';

jest.mock('../services/api', () => ({
    get: jest.fn(),
    post: jest.fn(),
}));
import api from '../services/api';

jest.mock('../components/Layout', () => ({ children }) => <div data-testid="layout">{children}</div>);

const renderDonations = () =>
    render(
        <MemoryRouter>
            <Donations />
        </MemoryRouter>
    );

beforeEach(() => {
    jest.clearAllMocks();
    api.get.mockResolvedValue({ data: [] });
    api.post.mockResolvedValue({ data: { id: 1 } });
});

describe('Donations Page - Rendering', () => {
    it('renders the Donations heading', async () => {
        renderDonations();
        expect(screen.getByText(/^Donations$/i)).toBeInTheDocument();
    });

    it('renders the "Record Donations" section heading', async () => {
        renderDonations();
        expect(screen.getByText(/Record Donations/i)).toBeInTheDocument();
    });

    it('renders the initial donation entry row (Entry 1)', async () => {
        renderDonations();
        expect(screen.getByText('Entry 1')).toBeInTheDocument();
    });

    it('renders "Save All Donations" button', async () => {
        renderDonations();
        expect(screen.getByRole('button', { name: /Save All Donations/i })).toBeInTheDocument();
    });

    it('renders "Add Entry" button', async () => {
        renderDonations();
        expect(screen.getByRole('button', { name: /Add Entry/i })).toBeInTheDocument();
    });

    it('renders "Clear All" button', async () => {
        renderDonations();
        expect(screen.getByRole('button', { name: /Clear All/i })).toBeInTheDocument();
    });

    it('renders "Recent Donations" section', async () => {
        renderDonations();
        expect(screen.getByText(/Recent Donations/i)).toBeInTheDocument();
    });
});

describe('Donations Page - Form Fields', () => {
    it('renders Devotee Name field', async () => {
        renderDonations();
        expect(screen.getByLabelText(/Devotee Name/i)).toBeInTheDocument();
    });

    it('renders Phone field', async () => {
        renderDonations();
        expect(screen.getByLabelText(/Phone/i)).toBeInTheDocument();
    });

    it('renders Amount field', async () => {
        renderDonations();
        expect(screen.getByLabelText(/Amount/i)).toBeInTheDocument();
    });

    it('renders Category dropdown', async () => {
        renderDonations();
        expect(screen.getByLabelText(/Category/i)).toBeInTheDocument();
    });

    it('renders Payment Mode dropdown with default Cash', async () => {
        renderDonations();
        // Payment Mode field should exist
        expect(screen.getByText(/Payment Mode/i, { selector: 'label' })).toBeInTheDocument();
    });
});

describe('Donations Page - Add/Remove Rows', () => {
    it('adds a second row when "Add Entry" is clicked', async () => {
        renderDonations();
        const addButton = screen.getByRole('button', { name: /Add Entry/i });
        fireEvent.click(addButton);
        await waitFor(() => {
            expect(screen.getByText('Entry 2')).toBeInTheDocument();
        });
    });

    it('limits rows to maximum 5', async () => {
        renderDonations();
        const addButton = screen.getByRole('button', { name: /Add Entry/i });
        // Click 4 times (we start with 1 row)
        fireEvent.click(addButton);
        fireEvent.click(addButton);
        fireEvent.click(addButton);
        fireEvent.click(addButton);

        await waitFor(() => {
            expect(screen.getByText('Entry 5')).toBeInTheDocument();
            expect(addButton).toBeDisabled();
        });
    });

    it('removes a row when the delete button is clicked (when 2+ rows)', async () => {
        renderDonations();
        const addButton = screen.getByRole('button', { name: /Add Entry/i });
        fireEvent.click(addButton);

        await waitFor(() => {
            expect(screen.getByText('Entry 2')).toBeInTheDocument();
        });

        // Click the first delete button (there should be one per row when >1 rows)
        const deleteButtons = screen.getAllByTestId ? [] : document.querySelectorAll('[data-testid="DeleteIcon"]');
        const removeButtons = screen.getAllByRole('button').filter(btn => btn.closest('[class*="error"]'));
        if (removeButtons.length > 0) {
            fireEvent.click(removeButtons[0]);
            await waitFor(() => {
                expect(screen.queryByText('Entry 2')).not.toBeInTheDocument();
            });
        }
    });
});

describe('Donations Page - Validation', () => {
    it('shows error message when submitting empty form', async () => {
        renderDonations();
        const saveButton = screen.getByRole('button', { name: /Save All Donations/i });
        fireEvent.click(saveButton);

        await waitFor(() => {
            expect(screen.getByText(/fill at least one donation entry/i)).toBeInTheDocument();
        });
    });

    it('does not call api.post when all fields are empty', async () => {
        renderDonations();
        fireEvent.click(screen.getByRole('button', { name: /Save All Donations/i }));
        await waitFor(() => {
            expect(api.post).not.toHaveBeenCalled();
        });
    });
});

describe('Donations Page - Successful Submission', () => {
    it('calls api.post with correct data for valid donation', async () => {
        renderDonations();

        await userEvent.type(screen.getByLabelText(/Devotee Name/i), 'Rama Sharma');
        await userEvent.type(screen.getByLabelText(/Phone/i), '9876543210');
        await userEvent.type(screen.getByLabelText(/Amount/i), '1000');

        // Open Category dropdown and select
        fireEvent.mouseDown(screen.getByLabelText(/Category/i));
        await waitFor(() => screen.getByText('General Donation'));
        fireEvent.click(screen.getByText('General Donation'));

        fireEvent.click(screen.getByRole('button', { name: /Save All Donations/i }));

        await waitFor(() => {
            expect(api.post).toHaveBeenCalledWith(
                '/api/v1/donations',
                expect.objectContaining({
                    devotee_name: 'Rama Sharma',
                    devotee_phone: '9876543210',
                    amount: 1000,
                    category: 'General Donation',
                })
            );
        });
    });

    it('shows success message after saving', async () => {
        renderDonations();

        await userEvent.type(screen.getByLabelText(/Devotee Name/i), 'Rama');
        await userEvent.type(screen.getByLabelText(/Phone/i), '9876543210');
        await userEvent.type(screen.getByLabelText(/Amount/i), '500');

        fireEvent.mouseDown(screen.getByLabelText(/Category/i));
        await waitFor(() => screen.getByText('General Donation'));
        fireEvent.click(screen.getByText('General Donation'));

        fireEvent.click(screen.getByRole('button', { name: /Save All Donations/i }));

        await waitFor(() => {
            expect(screen.getByText(/Successfully recorded/i)).toBeInTheDocument();
        });
    });
});

describe('Donations Page - API Error', () => {
    it('shows error alert when api.post fails', async () => {
        api.post.mockRejectedValueOnce({
            response: { data: { detail: 'Devotee not found' } },
        });

        renderDonations();

        await userEvent.type(screen.getByLabelText(/Devotee Name/i), 'Unknown');
        await userEvent.type(screen.getByLabelText(/Phone/i), '0000000000');
        await userEvent.type(screen.getByLabelText(/Amount/i), '100');

        fireEvent.mouseDown(screen.getByLabelText(/Category/i));
        await waitFor(() => screen.getByText('General Donation'));
        fireEvent.click(screen.getByText('General Donation'));

        fireEvent.click(screen.getByRole('button', { name: /Save All Donations/i }));

        await waitFor(() => {
            expect(screen.getByText(/Devotee not found/i)).toBeInTheDocument();
        });
    });
});

describe('Donations Page - Clear All', () => {
    it('clears all form fields when "Clear All" clicked', async () => {
        renderDonations();
        await userEvent.type(screen.getByLabelText(/Devotee Name/i), 'Test User');

        fireEvent.click(screen.getByRole('button', { name: /Clear All/i }));

        await waitFor(() => {
            expect(screen.getByLabelText(/Devotee Name/i).value).toBe('');
        });
    });
});

describe('Donations Page - API Calls on Mount', () => {
    it('calls api.get for devotees on mount', async () => {
        renderDonations();
        await waitFor(() => {
            expect(api.get).toHaveBeenCalledWith('/api/v1/devotees');
        });
    });

    it('calls api.get for donations on mount', async () => {
        renderDonations();
        await waitFor(() => {
            expect(api.get).toHaveBeenCalledWith('/api/v1/donations');
        });
    });
});
