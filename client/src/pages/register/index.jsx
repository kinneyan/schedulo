import "./index.scss";

import NavigationBar from "../../components/navbar";
import RegisterContainer from "../../containers/register";

/**
 * Public registration page combining the navbar and registration form container.
 *
 * @returns {JSX.Element}
 */
const RegisterPage = () =>
{
    return (
        <div id="register-page">
            <NavigationBar />
            <div id="register-form-container">
                <RegisterContainer />
            </div>
        </div>
    );
};

export default RegisterPage;
