import React, {useState, useEffect} from 'react';
import Cookies from "universal-cookie";

import ViewProfile from '../../components/profile';

const Profile = () => 
{
    // get token from cookies
    const cookies = new Cookies();
    const token = cookies.get("token");

    // create states
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
                const response = await fetch(import.meta.env.VITE_API_URL + "/api/user", 
                {
                    method: "GET",
                    withCredentials: true,
                    credentials: "include",
                    headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token.access},
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

        // build request body
        let requestBody = {
            first_name: fname,
            last_name: lname,
            email: email,
            phone: phone,
        }

        if (newPassword !== "")
        {
            requestBody.current_password = oldPassword;
            requestBody.password = newPassword;
        }

        // make request
        try 
        {
            const response = await fetch(import.meta.env.VITE_API_URL + "/api/user", 
            {
                method: "PUT",
                withCredentials: true,
                credentials: "include",
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token.access},
                body: JSON.stringify(requestBody),
            });
            
            const data = await response.json();

            if (response.status === 400 && data.error.message == "Current password is incorrect.")
            {
                throw new Error("Current password is incorrect.");
            }

            if (response.status != 200)
            {
                throw new Error("Failed to update user information.");
            }

            window.location.reload();   // refresh page
        }
        catch (error)
        {
            console.log("Error: " + error);
        }

    };

    return (
        <div>
            <ViewProfile states={states} handleSubmit={handleSubmit}/>
        </div>
    );
};

export default Profile;
