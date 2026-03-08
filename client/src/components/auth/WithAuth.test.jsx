import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

// vi.hoisted ensures mockGet is initialized before vi.mock hoisting runs
const mockGet = vi.hoisted(() => vi.fn());

vi.mock('jwt-decode', () => ({ jwtDecode: vi.fn() }));
vi.mock('universal-cookie', () => ({
    default: vi.fn(function () { return { get: mockGet, remove: vi.fn() }; }),
}));

import { jwtDecode } from 'jwt-decode';
import withAuth from './WithAuth';

const DummyComponent = () => <div>Protected Content</div>;
const ProtectedComponent = withAuth(DummyComponent);

const renderWithRouter = () =>
    render(
        <MemoryRouter>
            <ProtectedComponent />
        </MemoryRouter>
    );

describe('withAuth', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders the wrapped component when a valid non-expired token is present', () => {
        mockGet.mockReturnValue({ access: 'valid.jwt.token' });
        jwtDecode.mockReturnValue({ exp: Math.floor(Date.now() / 1000) + 3600 });

        renderWithRouter();

        expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('does not call jwtDecode when no cookie is present', () => {
        mockGet.mockReturnValue(undefined);

        renderWithRouter();

        expect(mockGet).toHaveBeenCalledWith('token');
        expect(jwtDecode).not.toHaveBeenCalled();
    });

    it('calls jwtDecode to validate the token when a cookie is present', () => {
        mockGet.mockReturnValue({ access: 'expired.jwt.token' });
        jwtDecode.mockReturnValue({ exp: Math.floor(Date.now() / 1000) - 1 });

        renderWithRouter();

        expect(mockGet).toHaveBeenCalledWith('token');
        expect(jwtDecode).toHaveBeenCalledWith('expired.jwt.token');
    });
});
