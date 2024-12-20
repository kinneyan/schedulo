import React from 'react';
import './index.scss';

import NavigationBar from '../../components/navbar';
import LoginContainer from '../../containers/login';

const LoginPage = () => {
    return (
        <div id="login-page">
            <NavigationBar />
            <div id="login-form-container">
                    <LoginContainer />
            </div>
        </div>
    );
};

export default LoginPage;
