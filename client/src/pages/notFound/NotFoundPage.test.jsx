import {render, screen} from "@testing-library/react";
import {describe, it, expect} from "vitest";
import {MemoryRouter} from "react-router-dom";
import NotFoundPage from "./NotFoundPage";

describe("NotFoundPage", () =>
{
    it("renders a 404 heading", () =>
    {
        render(<MemoryRouter><NotFoundPage /></MemoryRouter>);
        expect(screen.getByRole("heading", {name: /404/})).toBeInTheDocument();
    });

    it("renders a link back to the home page", () =>
    {
        render(<MemoryRouter><NotFoundPage /></MemoryRouter>);
        expect(screen.getByRole("link", {name: /go home/i})).toBeInTheDocument();
    });
});
