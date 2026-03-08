import "./index.scss";

import withAuth from "../../components/auth";
import NavbarContainer from "../../containers/navbar";
import Profile from "../../containers/profile";

/**
 * User profile/settings page, protected by authentication.
 *
 * @returns {JSX.Element}
 */
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
