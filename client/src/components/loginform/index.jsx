import Container from 'react-bootstrap/Container';
import SubmitButton from '../submitbutton';

import "./index.scss";

const LoginForm = () => {
    return (
        <Container id="login-container">
            <form id="login-form">
                <label id="email-label">Email</label>
                <input type="email" name="email"  id="email-form"/>
                <label id="password-label">Password</label>
                <input type="password" name="password" id="password-form"/>
                <SubmitButton button_text="Log in" />
                <hr />
                <p>Don't have an account? <a href="#">Sign up</a></p>
            </form>
        </Container>
    );
};

export default LoginForm;
