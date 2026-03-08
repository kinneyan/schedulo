import Container from "react-bootstrap/Container";
import PropTypes from "prop-types";
import SubmitButton from "../../buttons/submitButton/SubmitButton";
import "./index.scss";

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
        <Container id="login-container">
            <form id="login-form" onSubmit={handleSubmit}>
                <label id="email-label" htmlFor="email-form">Email</label>
                <input
                    type="email"
                    name="email"
                    id="email-form"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <label id="password-label" htmlFor="password-form">Password</label>
                <input
                    type="password"
                    name="password"
                    id="password-form"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <SubmitButton buttonText="Log in" />
                {error && <div id="error-container">
                    <p id="error-text">{error}</p>
                </div>}
                <hr />
                <p>Don&#39;t have an account? <a href="register">Sign up</a></p>
            </form>
        </Container>
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
