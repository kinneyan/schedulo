import {render, screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {describe, it, expect, vi, beforeEach} from "vitest";
import {MemoryRouter} from "react-router-dom";
import NavigationBar from "./NavigationBar";

vi.mock("universal-cookie", () => 
{
    const mockRemove = vi.fn();
    const MockCookies = vi.fn(function () 
    {
        return {remove: mockRemove}; 
    });
    MockCookies._mockRemove = mockRemove;
    return {default: MockCookies};
});

const renderWithRouter = (ui) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe("NavigationBar", () => 
{
    beforeEach(() => 
    {
        vi.clearAllMocks();
    });

    it("renders the brand name \"Schedulo\"", () => 
    {
        renderWithRouter(<NavigationBar loggedIn={false} />);
        expect(screen.getByText("Schedulo")).toBeInTheDocument();
    });

    it("renders Home and About nav links", () => 
    {
        renderWithRouter(<NavigationBar loggedIn={false} />);
        expect(screen.getByText("Home")).toBeInTheDocument();
        expect(screen.getByText("About")).toBeInTheDocument();
    });

    it("does not show the Account dropdown when loggedIn=false", () =>
    {
        renderWithRouter(<NavigationBar loggedIn={false} />);
        expect(screen.queryByText("Account")).not.toBeInTheDocument();
    });

    it("shows Dashboard, Settings, and Log out links in the Account dropdown when loggedIn=true", async () => 
    {
        renderWithRouter(<NavigationBar loggedIn={true} />);
        await userEvent.click(screen.getByText("Account"));
        expect(screen.getByRole("link", {name: /dashboard/i})).toBeInTheDocument();
        expect(screen.getByRole("link", {name: /settings/i})).toBeInTheDocument();
        expect(screen.getByRole("link", {name: /log out/i})).toBeInTheDocument();
    });

    it("removes the token cookie when \"Log out\" is clicked", async () => 
    {
        const Cookies = (await import("universal-cookie")).default;
        renderWithRouter(<NavigationBar loggedIn={true} />);
        await userEvent.click(screen.getByText("Account"));
        await userEvent.click(screen.getByRole("link", {name: /log out/i}));
        const instance = Cookies.mock.results[0].value;
        expect(instance.remove).toHaveBeenCalledWith("token");
    });
});
