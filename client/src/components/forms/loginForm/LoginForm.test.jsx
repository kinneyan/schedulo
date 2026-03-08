import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import LoginForm from './LoginForm';

const defaultProps = {
    email: '',
    setEmail: vi.fn(),
    password: '',
    setPassword: vi.fn(),
    error: '',
    handleSubmit: vi.fn(),
};

describe('LoginForm', () => {
    it('renders email and password inputs', () => {
        render(<LoginForm {...defaultProps} />);
        expect(screen.getByLabelText('Email')).toBeInTheDocument();
        expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    it('renders the submit button', () => {
        render(<LoginForm {...defaultProps} />);
        expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
    });

    it('calls setEmail when the email input changes', async () => {
        const setEmail = vi.fn();
        render(<LoginForm {...defaultProps} setEmail={setEmail} />);
        await userEvent.type(screen.getByLabelText('Email'), 'a');
        expect(setEmail).toHaveBeenCalled();
    });

    it('calls setPassword when the password input changes', async () => {
        const setPassword = vi.fn();
        render(<LoginForm {...defaultProps} setPassword={setPassword} />);
        await userEvent.type(screen.getByLabelText('Password'), 'a');
        expect(setPassword).toHaveBeenCalled();
    });

    it('does not render an error message when error is empty', () => {
        render(<LoginForm {...defaultProps} error="" />);
        expect(screen.queryByText('Incorrect email or password')).not.toBeInTheDocument();
    });

    it('renders the error message when error is set', () => {
        render(<LoginForm {...defaultProps} error="Incorrect email or password" />);
        expect(screen.getByText('Incorrect email or password')).toBeInTheDocument();
    });

    it('calls handleSubmit when the form is submitted', async () => {
        const handleSubmit = vi.fn((e) => e.preventDefault());
        // Provide non-empty values so HTML5 required validation passes
        render(<LoginForm
            {...defaultProps}
            email="test@example.com"
            password="password123"
            handleSubmit={handleSubmit}
        />);
        await userEvent.click(screen.getByRole('button', { name: /log in/i }));
        expect(handleSubmit).toHaveBeenCalledOnce();
    });
});
