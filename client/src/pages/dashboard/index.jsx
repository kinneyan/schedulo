import "./index.scss";

import NavbarContainer from "../../containers/navbar";
import withAuth from "../../components/auth";

const DashboardPage = () => 
{
    return (
        <div id="dash-page">
            <NavbarContainer />
        </div>
    );
};

export default withAuth(DashboardPage);
