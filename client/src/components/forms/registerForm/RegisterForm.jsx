import Container from "react-bootstrap/Container";
import PropTypes from "prop-types";
import SubmitButton from "../../buttons/submitButton/SubmitButton";
import "./index.scss";

/**
 * Presentational registration form collecting user account details.
 *
 * @param {Object} props
 * @param {string} props.email - Current value of the email field.
 * @param {Function} props.setEmail - State setter for the email field.
 * @param {string} props.password - Current value of the password field.
 * @param {Function} props.setPassword - State setter for the password field.
 * @param {string} props.confirmPassword - Current value of the confirm-password field.
 * @param {Function} props.setConfirmPassword - State setter for the confirm-password field.
 * @param {string} props.firstName - Current value of the first name field.
 * @param {Function} props.setFirstName - State setter for the first name field.
 * @param {string} props.lastName - Current value of the last name field.
 * @param {Function} props.setLastName - State setter for the last name field.
 * @param {string} props.phone - Current value of the phone number field.
 * @param {Function} props.setPhone - State setter for the phone number field.
 * @param {string} [props.error] - Error message to display beneath the form, if any.
 * @param {Function} props.handleSubmit - Form submit handler.
 * @returns {JSX.Element}
 */
const RegisterForm = ({email, setEmail, password, setPassword, confirmPassword, setConfirmPassword, firstName, setFirstName, lastName, setLastName, phone, setPhone, error, handleSubmit}) =>
{
    return (
        <Container id="register-container">
            <form id="register-form" onSubmit={handleSubmit}>
                <label id="first-name-label" htmlFor="first-name-form">First Name</label>
                <input
                    type="text"
                    name="first-name"
                    id="first-name-form"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                />
                <label id="last-name-label" htmlFor="last-name-form">Last Name</label>
                <input
                    type="text"
                    name="last-name"
                    id="last-name-form"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                />
                <label id="email-label" htmlFor="email-form">Email</label>
                <input
                    type="email"
                    name="email"
                    id="email-form"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <label id="phone-label" htmlFor="phone-form">Phone Number</label>
                <input
                    type="tel"
                    name="phone"
                    id="phone-form"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
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
                <label id="confirm-password-label" htmlFor="confirm-password-form">Confirm Password</label>
                <input
                    type="password"
                    name="confirm-password"
                    id="confirm-password-form"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                />
                <SubmitButton buttonText="Sign up" />
                {error && <div id="error-container">
                    <p id="error-text">{error}</p>
                </div>}
                <hr />
                <p>Already have an account? <a href="login">Log in</a></p>
            </form>
        </Container>
    );
};

RegisterForm.propTypes = {
    email: PropTypes.string.isRequired,
    setEmail: PropTypes.func.isRequired,
    password: PropTypes.string.isRequired,
    setPassword: PropTypes.func.isRequired,
    confirmPassword: PropTypes.string.isRequired,
    setConfirmPassword: PropTypes.func.isRequired,
    firstName: PropTypes.string.isRequired,
    setFirstName: PropTypes.func.isRequired,
    lastName: PropTypes.string.isRequired,
    setLastName: PropTypes.func.isRequired,
    phone: PropTypes.string.isRequired,
    setPhone: PropTypes.func.isRequired,
    error: PropTypes.string,
    handleSubmit: PropTypes.func.isRequired,
};

export default RegisterForm;
