import {render, screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {describe, it, expect, vi, beforeEach} from "vitest";
import {MemoryRouter} from "react-router-dom";

const mockGet = vi.hoisted(() => vi.fn());

vi.mock("universal-cookie", () => ({
    default: vi.fn(function () 
    {
        return {get: mockGet, remove: vi.fn()}; 
    }),
}));

import NavbarContainer from "./NavbarContainer";

const renderWithRouter = () =>
    render(
        <MemoryRouter>
            <NavbarContainer />
        </MemoryRouter>,
    );

describe("NavbarContainer", () => 
{
    beforeEach(() => 
    {
        vi.clearAllMocks();
    });

    it("does not show the Account dropdown when no token cookie is present", () =>
    {
        mockGet.mockReturnValue(undefined);
        renderWithRouter();

        expect(screen.queryByText("Account")).not.toBeInTheDocument();
    });

    it("shows \"Log out\" in the Account dropdown when a token cookie is present", async () => 
    {
        mockGet.mockReturnValue({access: "some.jwt.token"});
        renderWithRouter();

        await userEvent.click(screen.getByText("Account"));
        expect(screen.getByText("Log out")).toBeInTheDocument();
    });
});
