import React, { useState } from 'react';
import LoginForm from '../../components/registerform';
import Cookies from 'universal-cookie';
import { Navigate } from 'react-router-dom';
import RegisterForm from '../../components/registerform';

const RegisterContainer = () => {
    const [email, setEmail] = useState('');
    const [first_name, setfirst_name] = useState('');
    const [last_name, setlast_name] = useState('');
    const [phone, setPhone] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [registered, setRegistered] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault(); // stop default form submission

        try {
            if (password == confirmPassword) {
                const response = await fetch(import.meta.env.VITE_API_URL + '/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password, first_name, last_name, phone }),
                });

                const data = await response.json();            
                const body = {
                    'access': data['access'],
                    'refresh': data['refresh'],
                };

                // catch error
                if (response.status != 201) {     
                    console.log(data['error']['message']); 
                    throw new Error(data['error']['message']);
                };

                // save cookie
                const cookies = new Cookies();
                cookies.set('token', JSON.stringify(body), {
                    path: '/' , 
                    sameSite: 'Lax',
                    expires: new Date(Date.now() + 86400000), // Set to 1 day
                });               

                // redirect
                setRegistered(true);
            } else {
                console.log("Password do not match");
                throw new Error("Passwords do not match");
            }
        } catch (error) {
            setError(error.message); 
        }
    };

    return (
        <div>
            <RegisterForm
                email={email}
                setEmail={setEmail}
                first_name={first_name}
                setfirst_name={setfirst_name}
                last_name={last_name}
                setlast_name={setlast_name}
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
        </div> // maybe want to redirect to an account created successfully page instead?
    );
};

export default RegisterContainer;