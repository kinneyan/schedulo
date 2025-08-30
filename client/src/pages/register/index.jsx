import "./index.scss";

import NavigationBar from "../../components/navbar";
import RegisterContainer from "../../containers/register";

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
