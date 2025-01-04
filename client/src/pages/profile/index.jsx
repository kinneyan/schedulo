import React from 'react';
import './index.scss';

import NavbarContainer from '../../containers/navbar';
import with_auth from '../../components/auth';

const ProfilePage = () => {
    return (
        <div>
            <NavbarContainer />
        </div>
    );
};

export default with_auth(ProfilePage);
