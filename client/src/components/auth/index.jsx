import {useEffect} from "react";
import {useNavigate} from "react-router-dom";
import {jwtDecode} from "jwt-decode";
import Cookies from "universal-cookie";

const withAuth = (WrappedComponent) => 
{
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
