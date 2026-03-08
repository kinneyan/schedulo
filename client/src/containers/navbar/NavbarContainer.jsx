import {useState, useEffect} from "react";
import Cookies from "universal-cookie";

import NavigationBar from "../../components/navbar/NavigationBar";

/**
 * Stateful container that checks the auth cookie and passes login state down to NavigationBar.
 *
 * @returns {JSX.Element}
 */
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
