import React from 'react';
import './index.scss';

import NavigationBar from '../../components/navbar';
import LoginContainer from '../../containers/register';
import RegisterContainer from '../../containers/register';

const RegisterPage = () => {
    return (
        <div id="register-page">
            <NavigationBar />
            <div id="register-form-container">
                    <RegisterContainer />
            </div>
        </div>
    );
};

export default RegisterPage;
