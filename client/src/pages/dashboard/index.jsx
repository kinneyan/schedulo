import "./index.scss";

import NavbarContainer from "../../containers/navbar";
import withAuth from "../../components/auth";

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
