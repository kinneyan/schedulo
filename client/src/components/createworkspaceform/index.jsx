import React from 'react';
import Container from 'react-bootstrap/Container';
import SubmitButton from '../submitbutton';
import "./index.scss";

const CreateWorkspaceForm = ({ name, setName, error, handleSubmit }) => {
    return (
        <Container id="create-workspace-container">
            <form id="create-workspace-form" onSubmit={handleSubmit}>
                <h>Create a new workspace</h>
                <label id="name-label">Workspace Name</label>
                <input
                    type="text"
                    name="name"
                    id="name-form"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
                <SubmitButton button_text="Create Workspace" />
                {error && <div id="error-container">
                    <p id="error-text">{error}</p>
                </div>}
            </form>
        </Container>
    );
};

export default CreateWorkspaceForm;