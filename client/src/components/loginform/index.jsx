import Container from "react-bootstrap/Container";
import PropTypes from "prop-types";
import SubmitButton from "../submitbutton";
import "./index.scss";

const LoginForm = ({email, setEmail, password, setPassword, error, handleSubmit}) => 
{
    return (
        <Container id="login-container">
            <form id="login-form" onSubmit={handleSubmit}>
                <label id="email-label">Email</label>
                <input
                    type="email"
                    name="email"
                    id="email-form"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
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
