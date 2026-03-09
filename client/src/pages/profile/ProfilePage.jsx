import "./index.scss";

import withAuth from "../../components/auth/WithAuth";
import NavbarContainer from "../../containers/navbar/NavbarContainer";
import Profile from "../../containers/profile/Profile";

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
