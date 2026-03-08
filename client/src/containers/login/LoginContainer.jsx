import {useState} from "react";
import LoginForm from "../../components/forms/loginForm/LoginForm";
import Cookies from "universal-cookie";
import {Navigate} from "react-router-dom";

/**
 * Stateful container that manages login form state, API submission, and post-login redirect.
 *
 * @returns {JSX.Element}
 */
const LoginContainer = () =>
{
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loggedIn, setLoggedIn] = useState(false);

    /**
     * Authenticates the user against the API and stores the returned JWT in a cookie.
     *
     * @param {React.FormEvent<HTMLFormElement>} e - The form submission event.
     * @returns {Promise<void>}
     */
    const handleSubmit = async (e) =>
    {
        e.preventDefault();

        try
        {
            const response = await fetch(import.meta.env.VITE_API_URL + "/api/login", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email, password}),
            });

            if (response.status !== 200)
            {
                throw new Error("Incorrect email or password");
            }

            const data = await response.json();

            const body = {
                access: data.access,
                refresh: data.refresh,
            };

            const cookies = new Cookies();
            cookies.set("token", JSON.stringify(body), {
                path: "/",
                sameSite: "Lax",
                expires: new Date(Date.now() + 86400000),
            });

            setLoggedIn(true);
        }
        catch
        {
            setError("Incorrect email or password");
        }
    };

    return (
        <div>
            <LoginForm
                email={email}
                setEmail={setEmail}
                password={password}
                setPassword={setPassword}
                error={error}
                handleSubmit={handleSubmit}
            />
            {loggedIn && <Navigate to="/dashboard" />}
        </div>
    );
};

export default LoginContainer;
