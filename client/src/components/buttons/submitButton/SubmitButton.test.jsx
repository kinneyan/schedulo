import {render, screen} from "@testing-library/react";
import {describe, it, expect} from "vitest";
import SubmitButton from "./SubmitButton";

describe("SubmitButton", () => 
{
    it("renders with the provided buttonText", () => 
    {
        render(<SubmitButton buttonText="Save" />);
        expect(screen.getByText("Save")).toBeInTheDocument();
    });

    it("has type=\"submit\"", () => 
    {
        render(<SubmitButton buttonText="Save" />);
        expect(screen.getByRole("button", {name: "Save"})).toHaveAttribute("type", "submit");
    });
});
