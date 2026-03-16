import NavbarContainer from "../../containers/navbar/NavbarContainer";
import WithAuth from "../../components/auth/WithAuth";

/**
 * Main authenticated dashboard page.
 *
 * @returns {JSX.Element}
 */
const DashboardPage = () =>
{
    return (
        <div>
            <NavbarContainer />
            <div className="max-w-screen-lg mx-auto px-4 py-8">
                <h1 className="text-2xl font-semibold">Dashboard</h1>
            </div>
        </div>
    );
};

export default WithAuth(DashboardPage);
