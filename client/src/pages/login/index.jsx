import React from 'react';
import './index.scss';

import NavigationBar from '../../components/navbar';
import LoginForm from '../../components/loginform';

const Login = () => {
    return (
        <div id="login-page">
            <NavigationBar />
            <div id="login-form-container">
                    <LoginForm />
            </div>
        </div>
    );
};

export default Login;
