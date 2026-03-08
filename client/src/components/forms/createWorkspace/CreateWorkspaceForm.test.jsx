import {render, screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {describe, it, expect, vi} from "vitest";
import CreateWorkspaceForm from "./CreateWorkspaceForm";

const defaultProps = {
    name: "",
    setName: vi.fn(),
    handleSubmit: vi.fn(),
};

describe("CreateWorkspaceForm", () => 
{
    it("renders the workspace name input", () => 
    {
        render(<CreateWorkspaceForm {...defaultProps} />);
        expect(screen.getByLabelText("Workspace Name")).toBeInTheDocument();
    });

    it("renders the submit button with text \"Create Workspace\"", () => 
    {
        render(<CreateWorkspaceForm {...defaultProps} />);
        expect(screen.getByRole("button", {name: "Create Workspace"})).toBeInTheDocument();
    });

    it("calls setName when the name input changes", async () => 
    {
        const setName = vi.fn();
        const user = userEvent.setup();
        render(<CreateWorkspaceForm {...defaultProps} setName={setName} />);
        await user.type(screen.getByLabelText("Workspace Name"), "My Workspace");
        expect(setName).toHaveBeenCalled();
    });

    it("does not render an error message when error is empty", () => 
    {
        render(<CreateWorkspaceForm {...defaultProps} />);
        expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it("renders the error message when error is set", () => 
    {
        render(<CreateWorkspaceForm {...defaultProps} error="Something went wrong" />);
        expect(screen.queryByText("Something went wrong")).toBeInTheDocument();
    });

    it("calls handleSubmit when the form is submitted", async () => 
    {
        const handleSubmit = vi.fn((e) => e.preventDefault());
        const user = userEvent.setup();
        render(<CreateWorkspaceForm {...defaultProps} name="My Workspace" handleSubmit={handleSubmit} />);
        await user.click(screen.getByRole("button", {name: "Create Workspace"}));
        expect(handleSubmit).toHaveBeenCalled();
    });
});
