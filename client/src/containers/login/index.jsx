import React, { useState } from 'react';
import LoginForm from '../../components/loginform';

const LoginContainer = () =>{
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault(); // stop default form submission

        try {
            const response = await fetch(import.meta.env.VITE_API_URL + '/api/login', { // Update the URL to your login endpoint
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            if (!response.ok) {
                throw new Error('Incorrect email or password');
            }

            // Handle successful login here (e.g., save token, redirect)
            console.log("WORKED");
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
