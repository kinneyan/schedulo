import React, { useState } from 'react';
import Cookies from 'universal-cookie';
import { Navigate } from 'react-router-dom';
import CreateWorkspaceForm from '../../components/createworkspaceform';

const CreateWorkspaceContainer = () =>{
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [created, setCreated] = useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault(); // stop default form submission

        try {
            // get token from cookies
            const cookies = new Cookies();
            const token = cookies.get('token');
            
            // request
            const response = await fetch(import.meta.env.VITE_API_URL + '/api/workspace/create/', {
                method: 'POST',
                withCredentials: true,
                credentials: 'include',
                headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token.access},
                body: JSON.stringify({ name }),
            });      
            
            const data = await response.json();  

            // catch error
            if (response.status == 400) {     
                console.log(data['error']['message']); 
                throw new Error(data['error']['message']);
            } else if (response.status != 201) {
                console.log(response.status); 
                throw new Error(response.status);
            };      

            // redirect
            setCreated(true);
            }
        catch (error) {
            setError(error.message); 
        }
    };

    return (
        <div>
            <CreateWorkspaceForm
                name={name}
                setName={setName}
                error={error}
                handleSubmit={handleSubmit}
            />
            {created && <Navigate to="/dashboard" />} 
        </div> // maybe redirect to the manage workspace page for this workspace
    );
}

export default CreateWorkspaceContainer;
