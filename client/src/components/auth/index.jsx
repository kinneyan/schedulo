import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode'
import Cookies from 'universal-cookie';

const with_auth = (WrappedComponent) => {
    // Auth wrapper to be used on pages that require authentication
    // 
    // Ex:
    //     export default with_auth(WrappedComponent);
    // 
    // Important:
    // Import and use within wrapped component, not here.

    return (props) => {
        const navigate = useNavigate();
        
        useEffect(() => {
            const cookies = new Cookies();
            const token = cookies.get('token');
            
            if (!token || !is_valid_token(token))
                {
                    navigate('/login');
                }
            }, [navigate]);
            
            return <WrappedComponent {...props} />;
        }
    };
    
const is_valid_token = (token) => {
    // not a comprehensive check, simply checks that the token is not expired
    try 
    {
        const decoded = jwtDecode(token.access);
        const exp = new Date(decoded.exp * 1000);
        const current = new Date();

        // token is not valid if exp timestamp is past current timestamp
        if (exp.getTime() < current.getTime()) return false;
    }
    catch
    {
        return false;
    }
    return true;
};

export default with_auth;
