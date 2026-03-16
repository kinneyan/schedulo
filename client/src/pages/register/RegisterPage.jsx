import NavbarContainer from "../../containers/navbar/NavbarContainer";
import RegisterContainer from "../../containers/register/RegisterContainer";

/**
 * Public registration page combining the navbar and registration form container.
 *
 * @returns {JSX.Element}
 */
const RegisterPage = () =>
{
    return (
        <div>
            <NavbarContainer />
            <div className="flex justify-center pt-16 px-4">
                <RegisterContainer />
            </div>
        </div>
    );
};

export default RegisterPage;
