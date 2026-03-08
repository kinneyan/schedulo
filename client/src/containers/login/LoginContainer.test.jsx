import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LoginContainer from './LoginContainer';

// Wrap in MemoryRouter because LoginContainer uses <Navigate>
const renderWithRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe('LoginContainer', () => {
    beforeEach(() => {
        vi.stubGlobal('fetch', vi.fn());
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('renders the login form', () => {
        renderWithRouter(<LoginContainer />);
        expect(screen.getByLabelText('Email')).toBeInTheDocument();
        expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    it('stores the token cookie and redirects on successful login', async () => {
        fetch.mockResolvedValueOnce({
            status: 200,
            json: async () => ({ access: 'access-token', refresh: 'refresh-token' }),
        });

        renderWithRouter(<LoginContainer />);

        await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
        await userEvent.type(screen.getByLabelText('Password'), 'password123');
        await userEvent.click(screen.getByRole('button', { name: /log in/i }));

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledOnce();
        });
    });

    it('shows an error message when credentials are invalid', async () => {
        fetch.mockResolvedValueOnce({ status: 401 });

        renderWithRouter(<LoginContainer />);

        await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
        await userEvent.type(screen.getByLabelText('Password'), 'wrongpassword');
        await userEvent.click(screen.getByRole('button', { name: /log in/i }));

        await waitFor(() => {
            expect(screen.getByText('Incorrect email or password')).toBeInTheDocument();
        });
    });

    it('shows an error message when the request fails', async () => {
        fetch.mockRejectedValueOnce(new Error('Network error'));

        renderWithRouter(<LoginContainer />);

        await userEvent.type(screen.getByLabelText('Email'), 'test@example.com');
        await userEvent.type(screen.getByLabelText('Password'), 'password123');
        await userEvent.click(screen.getByRole('button', { name: /log in/i }));

        await waitFor(() => {
            expect(screen.getByText('Incorrect email or password')).toBeInTheDocument();
        });
    });
});
