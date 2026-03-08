import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Profile from './Profile';

vi.mock('universal-cookie', () => {
    const mockGet = vi.fn().mockReturnValue({ access: 'test-token' });
    return { default: vi.fn(function () { return { get: mockGet, set: vi.fn() }; }) };
});

const userApiResponse = {
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '123',
};

beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
    fetch.mockResolvedValue({
        status: 200,
        json: async () => userApiResponse,
    });
    Object.defineProperty(window, 'location', {
        value: { reload: vi.fn() },
        writable: true,
    });
});

afterEach(() => {
    vi.restoreAllMocks();
});

describe('Profile', () => {
    it('renders account settings tab content with a Save button after data loads', async () => {
        render(<Profile />);

        await waitFor(() => {
            expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
        });
    });

    it('populates form fields with data fetched from the API on mount', async () => {
        render(<Profile />);

        await waitFor(() => {
            expect(screen.getByDisplayValue('John')).toBeInTheDocument();
            expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
            expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument();
            expect(screen.getByDisplayValue('123')).toBeInTheDocument();
        });
    });

    it('calls window.location.reload on successful profile update', async () => {
        const user = userEvent.setup();

        // Second fetch call (the PUT) returns success
        fetch
            .mockResolvedValueOnce({
                status: 200,
                json: async () => userApiResponse,
            })
            .mockResolvedValueOnce({
                status: 200,
                json: async () => ({}),
            });

        render(<Profile />);

        await waitFor(() => {
            expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
        });

        await user.click(screen.getByRole('button', { name: /save/i }));

        await waitFor(() => {
            expect(window.location.reload).toHaveBeenCalled();
        });
    });

    it('shows "Current password is incorrect." error when API returns that 400 message', async () => {
        const user = userEvent.setup();

        fetch
            .mockResolvedValueOnce({
                status: 200,
                json: async () => userApiResponse,
            })
            .mockResolvedValueOnce({
                status: 400,
                json: async () => ({ error: { message: 'Current password is incorrect.' } }),
            });

        render(<Profile />);

        await waitFor(() => {
            expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
        });

        await user.click(screen.getByRole('button', { name: /save/i }));

        await waitFor(() => {
            expect(screen.getByText(/Current password is incorrect\./i)).toBeInTheDocument();
        });
    });
});
