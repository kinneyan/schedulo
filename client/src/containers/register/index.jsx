import {useState} from "react";
import Cookies from "universal-cookie";
import {Navigate} from "react-router-dom";
import RegisterForm from "../../components/forms/registerForm";

const RegisterContainer = () => 
{
    const [email, setEmail] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [phone, setPhone] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [registered, setRegistered] = useState(false);

    const handleSubmit = async (e) => 
    {
        e.preventDefault();

        try 
        {
            if (password === confirmPassword) 
            {
                const response = await fetch(import.meta.env.VITE_API_URL + "/api/register", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({email, password, first_name: firstName, last_name: lastName, phone}),
                });

                const data = await response.json();            
                const body = {
                    access: data.access,
                    refresh: data.refresh,
                };

                if (response.status !== 201) 
                {     
                    console.log(data.error.message); 
                    throw new Error(data.error.message);
                }

                const cookies = new Cookies();
                cookies.set("token", JSON.stringify(body), {
                    path: "/",
                    sameSite: "Lax",
                    expires: new Date(Date.now() + 86400000),
                });

                setRegistered(true);
            }
            else 
            {
                console.log("Password do not match");
                throw new Error("Passwords do not match");
            }
        }
        catch (error) 
        {
            setError(error.message); 
        }
    };

    return (
        <div>
            <RegisterForm
                email={email}
                setEmail={setEmail}
                firstName={firstName}
                setFirstName={setFirstName}
                lastName={lastName}
                setLastName={setLastName}
                phone={phone}
                setPhone={setPhone}
                password={password}
                setPassword={setPassword}
                confirmPassword={confirmPassword}
                setConfirmPassword={setConfirmPassword}
                error={error}
                handleSubmit={handleSubmit}
            />
            {registered && <Navigate to="/dashboard" />} 
        </div>
    );
};

export default RegisterContainer;