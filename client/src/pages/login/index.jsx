import React from 'react';
import './index.scss';

import NavbarContainer from '../../containers/navbar';
import LoginContainer from '../../containers/login';

const LoginPage = () => 
{
    return (
        <div id="login-page">
            <NavbarContainer />
            <div id="login-form-container">
                    <LoginContainer />
            </div>
        </div>
    );
};

export default LoginPage;
