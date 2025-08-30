import Container from "react-bootstrap/Container";
import PropTypes from "prop-types";
import SubmitButton from "../../buttons/submitButton";
import "./index.scss";

const RegisterForm = ({email, setEmail, password, setPassword, confirmPassword, setConfirmPassword, firstName, setFirstName, lastName, setLastName, phone, setPhone, error, handleSubmit}) => 
{
    return (
        <Container id="register-container">
            <form id="register-form" onSubmit={handleSubmit}>
                <label id="first-name-label">First Name</label>
                <input
                    type="text"
                    name="first-name"
                    id="first-name-form"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    required
                />
                <label id="last-name-label">Last Name</label>
                <input
                    type="text"
                    name="last-name"
                    id="last-name-form"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    required
                />
                <label id="email-label">Email</label>
                <input
                    type="email"
                    name="email"
                    id="email-form"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <label id="phone-label">Phone Number</label>
                <input
                    type="tel"
                    name="phone"
                    id="phone-form"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                />
                <label id="password-label">Password</label>
                <input
                    type="password"
                    name="password"
                    id="password-form"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <label id="confirm-password-label">Confirm Password</label>
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