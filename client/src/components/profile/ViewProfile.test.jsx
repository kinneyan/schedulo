import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import ViewProfile from './ViewProfile';

const defaultStates = {
    fname: 'John', setFname: vi.fn(),
    lname: 'Doe', setLname: vi.fn(),
    email: 'john@example.com', setEmail: vi.fn(),
    phone: '1234567890', setPhone: vi.fn(),
    oldPassword: '', setOldPassword: vi.fn(),
    newPassword: '', setNewPassword: vi.fn(),
    error: '',
};

const renderComponent = (stateOverrides = {}, handleSubmit = vi.fn()) =>
    render(
        <ViewProfile
            states={{ ...defaultStates, ...stateOverrides }}
            handleSubmit={handleSubmit}
        />
    );

describe('ViewProfile', () => {
    it('renders both tab labels', () => {
        renderComponent();
        expect(screen.getByText('Account Settings')).toBeInTheDocument();
        expect(screen.getByText('Workspace Settings')).toBeInTheDocument();
    });

    it('shows the account form by default, including Save button', () => {
        renderComponent();
        expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
        expect(screen.getByText('Account Information')).toBeInTheDocument();
    });

    it('switches to workspace tab on click and shows placeholder text', async () => {
        renderComponent();
        await userEvent.click(screen.getByText('Workspace Settings'));
        expect(screen.getByText('Workspace settings will be implemented later.')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Save' })).not.toBeInTheDocument();
    });

    it('switches back to account tab after visiting workspace tab', async () => {
        renderComponent();
        await userEvent.click(screen.getByText('Workspace Settings'));
        await userEvent.click(screen.getByText('Account Settings'));
        expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument();
        expect(screen.queryByText('Workspace settings will be implemented later.')).not.toBeInTheDocument();
    });

    it('renders an error message when states.error is set', () => {
        renderComponent({ error: 'Something went wrong.' });
        expect(screen.getByText('Something went wrong.')).toBeInTheDocument();
    });

    it('does not render an error when states.error is empty', () => {
        const { container } = renderComponent({ error: '' });
        expect(container.querySelector('#error-container')).not.toBeInTheDocument();
    });
});
