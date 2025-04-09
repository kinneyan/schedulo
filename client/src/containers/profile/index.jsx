import React, {useState, useEffect} from 'react';
import Cookies from "universal-cookie";

import ViewProfile from '../../components/profile';

const Profile = () => 
{
    const [fname, setFname] = useState("");
    const [lname, setLname] = useState("");
    const [email, setEmail] = useState("");
    const [phone, setPhone] = useState("");
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const states = {
        fname,
        setFname,
        lname,
        setLname,
        email,
        setEmail,
        phone,
        setPhone,
        oldPassword,
        setOldPassword,
        newPassword,
        setNewPassword
    }

    useEffect(() => 
    {
        const fetchData = async () => 
        {
            // populate user information
            try 
            {
                // get token from cookies
                const cookies = new Cookies();
                const token = cookies.get("token");
        
                const response = await fetch(import.meta.env.VITE_API_URL + "/api/user", 
                {
                    method: "GET",
                    withCredentials: true,
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token.access},
                });
        
                const data = await response.json();
        
                if (response.status == 401)
                {
                    throw new Error("Failed to authorize request.");
                }

                setFname(data.first_name);
                setLname(data.last_name);
                setEmail(data.email);
                setPhone(data.phone);
            }
            catch (error)
            {
                console.log(error);
            }
        };

        fetchData();
    }, []);
    

    const handleSubmit = async (e) => 
    {
        e.preventDefault();     // stop default form submission

    };

    return (
        <div>
            <ViewProfile states={states} handleSubmit={handleSubmit}/>
        </div>
    );
};

export default Profile;
