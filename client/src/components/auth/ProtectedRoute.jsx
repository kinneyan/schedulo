import {Navigate, Outlet} from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import Cookies from "universal-cookie";

const isValidToken = (token) =>
{
    try
    {
        const decoded = jwtDecode(token.access);
        const exp = new Date(decoded.exp * 1000);
        return exp.getTime() >= new Date().getTime();
    }
    catch
    {
        return false;
    }
};

const ProtectedRoute = () =>
{
    const cookies = new Cookies();
    const token = cookies.get("token");

    if (!token || !isValidToken(token))
    {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
