import React, { useState } from 'react';
import Cookies from 'universal-cookie';
import { Navigate } from 'react-router-dom';
import CreateWorkspaceForm from '../../components/createworkspaceform';

const CreateWorkspaceContainer = () =>{
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    
    const handleSubmit = async (e) => {

    }

    return (
        <div>
            <CreateWorkspaceForm
                email={name}
                setEmail={setName}
                error={error}
                handleSubmit={handleSubmit}
            />
        </div>
    );
}

export default CreateWorkspaceContainer;