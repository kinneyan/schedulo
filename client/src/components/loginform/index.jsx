import React from 'react';
import Container from 'react-bootstrap/Container';
import SubmitButton from '../submitbutton';
import "./index.scss";

const LoginForm = ({ email, setEmail, password, setPassword, error, handleSubmit }) => {
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
                <SubmitButton button_text="Log in" />
                {error && <div id="error-container">
                    <p id="error-text">{error}</p>
                </div>}
                <hr />
                <p>Don't have an account? <a href="#">Sign up</a></p>
            </form>
        </Container>
    );
};

export default LoginForm;
