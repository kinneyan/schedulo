import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import CreateWorkspaceContainer from './CreateWorkspaceContainer';

vi.mock('universal-cookie', () => {
    const mockGet = vi.fn().mockReturnValue({ access: 'test-token' });
    return { default: vi.fn(function () { return { get: mockGet, set: vi.fn(), remove: vi.fn() }; }) };
});

const renderWithRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe('CreateWorkspaceContainer', () => {
    beforeEach(() => { vi.stubGlobal('fetch', vi.fn()); });
    afterEach(() => { vi.restoreAllMocks(); });

    it('renders the workspace name input and submit button', () => {
        renderWithRouter(<CreateWorkspaceContainer />);

        expect(screen.getByLabelText('Workspace Name')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Create Workspace' })).toBeInTheDocument();
    });

    it('calls fetch when the form is submitted with a name', async () => {
        fetch.mockResolvedValueOnce({
            status: 201,
            json: async () => ({}),
        });

        renderWithRouter(<CreateWorkspaceContainer />);

        await userEvent.type(screen.getByLabelText('Workspace Name'), 'My Workspace');
        await userEvent.click(screen.getByRole('button', { name: 'Create Workspace' }));

        await waitFor(() => {
            expect(fetch).toHaveBeenCalledOnce();
            expect(fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/workspace/create/'),
                expect.objectContaining({
                    method: 'POST',
                    body: JSON.stringify({ name: 'My Workspace' }),
                })
            );
        });
    });

    it('shows an error message when the API returns 400', async () => {
        fetch.mockResolvedValueOnce({
            status: 400,
            json: async () => ({ error: { message: 'Workspace name already exists' } }),
        });

        renderWithRouter(<CreateWorkspaceContainer />);

        await userEvent.type(screen.getByLabelText('Workspace Name'), 'Taken Name');
        await userEvent.click(screen.getByRole('button', { name: 'Create Workspace' }));

        await waitFor(() => {
            expect(screen.getByText('Workspace name already exists')).toBeInTheDocument();
        });
    });

    it('shows an error message when the request fails due to a network error', async () => {
        fetch.mockRejectedValueOnce(new Error('Network error'));

        renderWithRouter(<CreateWorkspaceContainer />);

        await userEvent.type(screen.getByLabelText('Workspace Name'), 'Any Name');
        await userEvent.click(screen.getByRole('button', { name: 'Create Workspace' }));

        await waitFor(() => {
            expect(screen.getByText('Network error')).toBeInTheDocument();
        });
    });
});
