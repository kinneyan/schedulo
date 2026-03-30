import {render, screen} from "@testing-library/react";
import {describe, it, expect, vi, beforeEach} from "vitest";
import {MemoryRouter, Routes, Route} from "react-router-dom";

const mockGet = vi.hoisted(() => vi.fn());

vi.mock("jwt-decode", () => ({jwtDecode: vi.fn()}));
vi.mock("universal-cookie", () => ({
    default: vi.fn(function ()
    {
        return {get: mockGet, remove: vi.fn()};
    }),
}));

import {jwtDecode} from "jwt-decode";
import ProtectedRoute from "./ProtectedRoute";

const renderWithRouter = (initialEntry = "/protected") =>
    render(
        <MemoryRouter initialEntries={[initialEntry]}>
            <Routes>
                <Route element={<ProtectedRoute />}>
                    <Route path="/protected" element={<div>Protected Content</div>} />
                </Route>
                <Route path="/login" element={<div>Login Page</div>} />
            </Routes>
        </MemoryRouter>,
    );

describe("ProtectedRoute", () =>
{
    beforeEach(() =>
    {
        vi.clearAllMocks();
    });

    it("renders child route when a valid non-expired token is present", () =>
    {
        mockGet.mockReturnValue({access: "valid.jwt.token"});
        jwtDecode.mockReturnValue({exp: Math.floor(Date.now() / 1000) + 3600});

        renderWithRouter();

        expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });

    it("redirects to /login when no token cookie is present", () =>
    {
        mockGet.mockReturnValue(undefined);

        renderWithRouter();

        expect(screen.getByText("Login Page")).toBeInTheDocument();
        expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("redirects to /login when the token is expired", () =>
    {
        mockGet.mockReturnValue({access: "expired.jwt.token"});
        jwtDecode.mockReturnValue({exp: Math.floor(Date.now() / 1000) - 1});

        renderWithRouter();

        expect(screen.getByText("Login Page")).toBeInTheDocument();
        expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
    });

    it("does not call jwtDecode when no cookie is present", () =>
    {
        mockGet.mockReturnValue(undefined);

        renderWithRouter();

        expect(mockGet).toHaveBeenCalledWith("token");
        expect(jwtDecode).not.toHaveBeenCalled();
    });
});
