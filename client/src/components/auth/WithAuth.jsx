import {useEffect} from "react";
import {useNavigate} from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import Cookies from "universal-cookie";

/**
 * Higher-order component that guards a route behind JWT authentication.
 * Redirects unauthenticated users to /login.
 *
 * @param {React.ComponentType} WrappedComponent - Component to render when the user is authenticated.
 * @returns {React.ComponentType} The wrapped component with authentication enforcement applied.
 */
const withAuth = (WrappedComponent) =>
{
    /**
     * Checks whether a JWT token is present and not yet expired.
     *
     * @param {{ access: string }} token - Token object containing the JWT access string.
     * @returns {boolean} True if the token is valid and unexpired, false otherwise.
     */
    const isValidToken = (token) =>
    {
        try
        {
            const decoded = jwtDecode(token.access);
            const exp = new Date(decoded.exp * 1000);
            const current = new Date();

            if (exp.getTime() < current.getTime()) return false;
        }
        catch
        {
            return false;
        }
        return true;
    };

    /**
     * Inner component that runs the auth check on mount and renders the wrapped component.
     *
     * @param {Object} props - Props forwarded to WrappedComponent.
     * @returns {JSX.Element}
     */
    const WrappedWithAuth = (props) =>
    {
        const navigate = useNavigate();

        useEffect(() =>
        {
            const cookies = new Cookies();
            const token = cookies.get("token");

            if (!token || !isValidToken(token))
            {
                navigate("/login");
            }
        }, [navigate]);

        return <WrappedComponent {...props} />;
    };

    return WrappedWithAuth;
};

export default withAuth;
