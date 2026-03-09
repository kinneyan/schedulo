import "./index.scss";

import NavbarContainer from "../../containers/navbar/NavbarContainer";

/**
 * Public home/landing page.
 *
 * @returns {JSX.Element}
 */
const HomePage = () =>
{
    return (
        <div id="home-page">
            <NavbarContainer />
        </div>
    );
};

export default HomePage;
