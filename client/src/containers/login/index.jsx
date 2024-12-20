import React, { useState } from 'react';
import LoginForm from '../../components/loginform';
import Cookies from 'universal-cookie';
import { redirect } from 'react-router-dom';

const LoginContainer = () =>{
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault(); // stop default form submission

        try {
            const response = fetch(import.meta.env.VITE_API_URL + '/api/login', { // Update the URL to your login endpoint
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            }).then((response) => response.json()).then((response) => {

                // save cookie
                const body = {
                    'access': response['access'],
                    'refresh': response['refresh'],
                }

                const cookies = new Cookies();
                cookies.set('token', JSON.stringify(body), {
                    path: '/' , 
                    sameSite: 'Lax',
                    expires: new Date(Date.now() + 86400000), // Set to 1 day
                });

                // redirect

            });


        } catch (error) {
            console.log("Error: ", error);
            setError("Incorrect email or password");
        }
    };

    return (
        <LoginForm
            email={email}
            setEmail={setEmail}
            password={password}
            setPassword={setPassword}
            error={error}
            handleSubmit={handleSubmit}
        />
    );
}

export default LoginContainer;
