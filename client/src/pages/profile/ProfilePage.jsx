import NavbarContainer from "../../containers/navbar/NavbarContainer";
import Profile from "../../containers/profile/Profile";

/**
 * Authenticated profile/settings page.
 *
 * @returns {JSX.Element}
 */
const ProfilePage = () =>
{
    return (
        <div>
            <NavbarContainer />
            <Profile />
        </div>
    );
};

export default ProfilePage;
