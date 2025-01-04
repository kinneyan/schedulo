import React from 'react';
import './index.scss';

import NavbarContainer from '../../containers/navbar';
import with_auth from '../../components/auth';

const DashboardPage = () => {
    return (
        <div id="dash-page">
            <NavbarContainer />
        </div>
    );
};

export default with_auth(DashboardPage);
