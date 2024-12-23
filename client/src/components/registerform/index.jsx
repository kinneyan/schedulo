import React from 'react';
import Container from 'react-bootstrap/Container';
import SubmitButton from '../submitbutton';
import "./index.scss";

const RegisterForm = ({email, setEmail, password, setPassword, confirmPassword, setConfirmPassword, first_name, setfirst_name, last_name, setlast_name, phone, setPhone, error, handleSubmit}) => {
    return (
        <Container id="register-container">
            <form id="register-form" onSubmit={handleSubmit}>
                <label id="first-name-label">First Name</label>
                <input
                    type="text"
                    name="first-name"
                    id="first-name-form"
                    value={first_name}
                    onChange={(e) => setfirst_name(e.target.value)}
                    required
                />
                <label id="last-name-label">Last Name</label>
                <input
                    type="text"
                    name="last-name"
                    id="last-name-form"
                    value={last_name}
                    onChange={(e) => setlast_name(e.target.value)}
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
                <SubmitButton button_text="Sign up" />
                {error && <div id="error-container">
                    <p id="error-text">{error}</p>
                </div>}
                <hr />
                <p>Already have an account? <a href="login">Log in</a></p>
            </form>
        </Container>
    );
};

export default RegisterForm;