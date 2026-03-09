import "./index.scss";

import NavbarContainer from "../../containers/navbar/NavbarContainer";
import withAuth from "../../components/auth/WithAuth";

/**
 * Main dashboard page, protected by authentication.
 *
 * @returns {JSX.Element}
 */
const DashboardPage = () =>
{
    return (
        <div id="dash-page">
            <NavbarContainer />
        </div>
    );
};

export default withAuth(DashboardPage);
