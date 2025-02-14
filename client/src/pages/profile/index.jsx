import React from 'react';
import './index.scss';

import with_auth from '../../components/auth';
import NavbarContainer from '../../containers/navbar';
import Profile from '../../containers/profile';

const ProfilePage = () => {
    return (
        <div>
            <NavbarContainer />
            <Profile />
        </div>
    );
};

export default with_auth(ProfilePage);
