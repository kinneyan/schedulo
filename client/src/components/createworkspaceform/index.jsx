import Container from "react-bootstrap/Container";
import SubmitButton from "../submitbutton";
import "./index.scss";
import PropTypes from "prop-types";

const CreateWorkspaceForm = ({name, setName, error, handleSubmit}) => 
{
    return (
        <Container id="create-workspace-container">
            <form id="create-workspace-form" onSubmit={handleSubmit}>
                <h1>Create a new workspace</h1>
                <label id="name-label">Workspace Name</label>
                <input
                    type="text"
                    name="name"
                    id="name-form"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                />
                <SubmitButton buttonText="Create Workspace" />
                {error && <div id="error-container">
                    <p id="error-text">{error}</p>
                </div>}
            </form>
        </Container>
    );
};

CreateWorkspaceForm.propTypes = {
    name: PropTypes.string.isRequired,
    setName: PropTypes.func.isRequired,
    error: PropTypes.string,
    handleSubmit: PropTypes.func.isRequired,
};

export default CreateWorkspaceForm;