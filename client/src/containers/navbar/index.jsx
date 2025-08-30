import {useState, useEffect} from "react";
import Cookies from "universal-cookie";

import NavigationBar from "../../components/navbar";

const NavbarContainer = () => 
{
    const [loggedIn, setLoggedIn] = useState(false);

    useEffect(() => 
    {
        const cookies = new Cookies();
        const token = cookies.get("token");
        if (token === undefined) 
        {
            setLoggedIn(false);
        }
        else 
        {
            setLoggedIn(true);
        }
    }, []);

    return (
        <div>
            <NavigationBar loggedIn={loggedIn} />
        </div>
    );
};

export default NavbarContainer;
