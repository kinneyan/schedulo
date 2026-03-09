import "./index.scss";

import NavbarContainer from "../../containers/navbar/NavbarContainer";
import LoginContainer from "../../containers/login/LoginContainer";

/**
 * Public login page combining the navbar and login form container.
 *
 * @returns {JSX.Element}
 */
const LoginPage = () =>
{
    return (
        <div id="login-page">
            <NavbarContainer />
            <div id="login-form-container">
                <LoginContainer />
            </div>
        </div>
    );
};

export default LoginPage;
