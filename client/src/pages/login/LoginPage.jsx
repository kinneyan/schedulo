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
        <div>
            <NavbarContainer />
            <div className="flex justify-center pt-16 px-4">
                <div className="w-full max-w-md">
                    <LoginContainer />
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
