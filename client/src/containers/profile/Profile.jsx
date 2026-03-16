import {useState, useEffect} from "react";
import Cookies from "universal-cookie";

import ViewProfile from "../../components/profile/ViewProfile";

/**
 * Stateful container that fetches the user's profile data and handles account update submissions.
 *
 * @returns {JSX.Element}
 */
const Profile = () =>
{
    const cookies = new Cookies();
    const token = cookies.get("token");

    const [fname, setFname] = useState("");
    const [lname, setLname] = useState("");
    const [email, setEmail] = useState("");
    const [phone, setPhone] = useState("");
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);
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
        setNewPassword,
        error,
        setError,
        success,
        setSuccess,
    };

    useEffect(() =>
    {
        /**
         * Fetches the authenticated user's profile data from the API and populates form state.
         *
         * @returns {Promise<void>}
         */
        const fetchData = async () =>
        {
            try
            {
                const response = await fetch(import.meta.env.VITE_API_URL + "/api/user", {
                    method: "GET",
                    withCredentials: true,
                    credentials: "include",
                    headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token.access},
                });

                const data = await response.json();

                if (response.status === 401)
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
    }, [token.access]);


    /**
     * Submits updated profile information to the API, including an optional password change.
     *
     * @param {React.FormEvent<HTMLFormElement>} e - The form submission event.
     * @returns {Promise<void>}
     */
    const handleSubmit = async (e) =>
    {
        e.preventDefault();

        let requestBody = {
            first_name: fname,
            last_name: lname,
            email: email,
            phone: phone,
        };

        if (newPassword !== "")
        {
            requestBody.current_password = oldPassword;
            requestBody.password = newPassword;
        }

        try
        {
            const response = await fetch(import.meta.env.VITE_API_URL + "/api/user", {
                method: "PUT",
                withCredentials: true,
                credentials: "include",
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token.access},
                body: JSON.stringify(requestBody),
            });

            const data = await response.json();

            if (response.status === 400 && data.error.message === "Current password is incorrect.")
            {
                throw new Error("Current password is incorrect.");
            }

            if (response.status !== 200)
            {
                throw new Error("Failed to update user information.");
            }

            setSuccess(true);
            setOldPassword("");
            setNewPassword("");
        }
        catch (error)
        {
            setError(error.message);
        }
    };

    return (
        <div>
            <ViewProfile states={states} handleSubmit={handleSubmit}/>
        </div>
    );
};

export default Profile;
