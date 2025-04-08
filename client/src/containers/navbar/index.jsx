import React, { useState, useEffect } from 'react';
import Cookies from 'universal-cookie';

import NavigationBar from '../../components/navbar';

const NavbarContainer = () => 
{
    const [logged_in, setLogged_in] = useState(false);

    useEffect(() => 
    {
        const cookies = new Cookies();
        const token = cookies.get('token');
        if (token == undefined)
        {
            setLogged_in(false);
        }
        else 
        {
            setLogged_in(true);
        }
    }, []);

    
    return (
        <div>
            <NavigationBar logged_in={logged_in} />
        </div>
    )
}

export default NavbarContainer;
