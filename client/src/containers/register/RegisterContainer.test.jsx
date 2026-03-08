import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import RegisterContainer from './RegisterContainer';

vi.mock('universal-cookie', () => {
    const mockSet = vi.fn();
    return { default: vi.fn(function () { return { get: vi.fn(), set: mockSet, remove: vi.fn() }; }) };
});

const renderWithRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

const fillForm = async ({ firstName = 'Jane', lastName = 'Doe', email = 'jane@example.com', phone = '5550001234', password = 'secret123', confirmPassword = 'secret123' } = {}) => {
    await userEvent.type(screen.getByLabelText('First Name'), firstName);
    await userEvent.type(screen.getByLabelText('Last Name'), lastName);
    await userEvent.type(screen.getByLabelText('Email'), email);
    await userEvent.type(screen.getByLabelText('Phone Number'), phone);
    await userEvent.type(screen.getByLabelText('Password'), password);
    await userEvent.type(screen.getByLabelText('Confirm Password'), confirmPassword);
};

describe('RegisterContainer', () => {
    beforeEach(() => { vi.stubGlobal('fetch', vi.fn()); });
    afterEach(() => { vi.restoreAllMocks(); });

    it('renders all registration form inputs', () => {
        renderWithRouter(<RegisterContainer />);

        expect(screen.getByLabelText('First Name')).toBeInTheDocument();
        expect(screen.getByLabelText('Last Name')).toBeInTheDocument();
        expect(screen.getByLabelText('Email')).toBeInTheDocument();
        expect(screen.getByLabelText('Phone Number')).toBeInTheDocument();
        expect(screen.getByLabelText('Password')).toBeInTheDocument();
        expect(screen.getByLabelText('Confirm Password')).toBeInTheDocument();
    });

    it('shows an error when passwords do not match', async () => {
        renderWithRouter(<RegisterContainer />);

        await fillForm({ password: 'secret123', confirmPassword: 'different' });
        await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));

        await waitFor(() => {
            expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
        });
        expect(fetch).not.toHaveBeenCalled();
    });

    it('calls fetch and stores a cookie on successful registration', async () => {
        fetch.mockResolvedValueOnce({
            status: 201,
            json: async () => ({ access: 'access-token', refresh: 'refresh-token' }),
        });

        renderWithRouter(<RegisterContainer />);

        await fillForm();
        await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledOnce();
            expect(fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/register'),
                expect.objectContaining({ method: 'POST' })
            );
        });

        const { default: Cookies } = await import('universal-cookie');
        const mockInstance = Cookies.mock.results[Cookies.mock.results.length - 1].value;
        expect(mockInstance.set).toHaveBeenCalledWith(
            'token',
            JSON.stringify({ access: 'access-token', refresh: 'refresh-token' }),
            expect.any(Object)
        );
    });

    it('shows an error when the API returns a non-201 status', async () => {
        fetch.mockResolvedValueOnce({
            status: 409,
            json: async () => ({ error: { message: 'Email already in use' } }),
        });

        renderWithRouter(<RegisterContainer />);

        await fillForm();
        await userEvent.click(screen.getByRole('button', { name: 'Sign up' }));

        await waitFor(() => {
            expect(screen.getByText('Email already in use')).toBeInTheDocument();
        });
    });
});
