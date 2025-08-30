import "./index.scss";

import withAuth from "../../components/auth";
import NavbarContainer from "../../containers/navbar";
import Profile from "../../containers/profile";

const ProfilePage = () => 
{
    return (
        <div id="profile-page">
            <NavbarContainer />
            <Profile />
        </div>
    );
};

export default withAuth(ProfilePage);
