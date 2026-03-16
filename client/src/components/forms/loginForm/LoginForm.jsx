import PropTypes from "prop-types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import SubmitButton from "../../buttons/submitButton/SubmitButton";

/**
 * Presentational login form with email and password fields.
 *
 * @param {Object} props
 * @param {string} props.email - Current value of the email field.
 * @param {Function} props.setEmail - State setter for the email field.
 * @param {string} props.password - Current value of the password field.
 * @param {Function} props.setPassword - State setter for the password field.
 * @param {string} [props.error] - Error message to display beneath the form, if any.
 * @param {Function} props.handleSubmit - Form submit handler.
 * @returns {JSX.Element}
 */
const LoginForm = ({email, setEmail, password, setPassword, error, handleSubmit}) =>
{
    return (
        <div className="w-full max-w-sm">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                    <Label htmlFor="email-form">Email</Label>
                    <Input
                        type="email"
                        name="email"
                        id="email-form"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="flex flex-col gap-1.5">
                    <Label htmlFor="password-form">Password</Label>
                    <Input
                        type="password"
                        name="password"
                        id="password-form"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <SubmitButton buttonText="Log in" />
                {error && (
                    <p className="text-destructive text-sm">{error}</p>
                )}
                <hr className="border-border" />
                <p className="text-sm text-center">
                    Don&#39;t have an account? <a href="register" className="text-primary underline">Sign up</a>
                </p>
            </form>
        </div>
    );
};

LoginForm.propTypes = {
    email: PropTypes.string.isRequired,
    setEmail: PropTypes.func.isRequired,
    password: PropTypes.string.isRequired,
    setPassword: PropTypes.func.isRequired,
    error: PropTypes.string,
    handleSubmit: PropTypes.func.isRequired,
};

export default LoginForm;
