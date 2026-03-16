import NavbarContainer from "../../containers/navbar/NavbarContainer";
import Profile from "../../containers/profile/Profile";
import WithAuth from "../../components/auth/WithAuth";

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

export default WithAuth(ProfilePage);
