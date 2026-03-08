import {render, screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {describe, it, expect, vi} from "vitest";
import RegisterForm from "./RegisterForm";

const defaultProps = {
    email: "",
    setEmail: vi.fn(),
    password: "",
    setPassword: vi.fn(),
    confirmPassword: "",
    setConfirmPassword: vi.fn(),
    firstName: "",
    setFirstName: vi.fn(),
    lastName: "",
    setLastName: vi.fn(),
    phone: "",
    setPhone: vi.fn(),
    handleSubmit: vi.fn(),
};

// Props with non-empty values so HTML5 required validation passes on submit.
const filledProps = {
    ...defaultProps,
    email: "test@example.com",
    password: "secret123",
    confirmPassword: "secret123",
    firstName: "Jane",
    lastName: "Doe",
    phone: "555-1234",
};

describe("RegisterForm", () => 
{
    it("renders all six inputs", () => 
    {
        render(<RegisterForm {...defaultProps} />);
        expect(screen.getByLabelText("First Name")).toBeInTheDocument();
        expect(screen.getByLabelText("Last Name")).toBeInTheDocument();
        expect(screen.getByLabelText("Email")).toBeInTheDocument();
        expect(screen.getByLabelText("Phone Number")).toBeInTheDocument();
        expect(screen.getByLabelText("Password")).toBeInTheDocument();
        expect(screen.getByLabelText("Confirm Password")).toBeInTheDocument();
    });

    it("renders the submit button with text \"Sign up\"", () => 
    {
        render(<RegisterForm {...defaultProps} />);
        expect(screen.getByRole("button", {name: "Sign up"})).toBeInTheDocument();
    });

    it("calls setFirstName when the first name input changes", async () => 
    {
        const setFirstName = vi.fn();
        const user = userEvent.setup();
        render(<RegisterForm {...defaultProps} setFirstName={setFirstName} />);
        await user.type(screen.getByLabelText("First Name"), "Jane");
        expect(setFirstName).toHaveBeenCalled();
    });

    it("calls setEmail when the email input changes", async () => 
    {
        const setEmail = vi.fn();
        const user = userEvent.setup();
        render(<RegisterForm {...defaultProps} setEmail={setEmail} />);
        await user.type(screen.getByLabelText("Email"), "test@example.com");
        expect(setEmail).toHaveBeenCalled();
    });

    it("does not render an error message when error is empty", () => 
    {
        render(<RegisterForm {...defaultProps} />);
        expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
    });

    it("renders the error message when error is set", () => 
    {
        render(<RegisterForm {...defaultProps} error="Registration failed" />);
        expect(screen.queryByText("Registration failed")).toBeInTheDocument();
    });

    it("calls handleSubmit when form is submitted", async () => 
    {
        const handleSubmit = vi.fn((e) => e.preventDefault());
        const user = userEvent.setup();
        render(<RegisterForm {...filledProps} handleSubmit={handleSubmit} />);
        await user.click(screen.getByRole("button", {name: "Sign up"}));
        expect(handleSubmit).toHaveBeenCalled();
    });
});
