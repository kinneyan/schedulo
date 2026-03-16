import PropTypes from "prop-types";
import {Input} from "@/components/ui/input";
import {Label} from "@/components/ui/label";
import SubmitButton from "../../buttons/submitButton/SubmitButton";

/**
 * Presentational form for creating a new workspace.
 *
 * @param {Object} props
 * @param {string} props.name - Current value of the workspace name field.
 * @param {Function} props.setName - State setter for the workspace name.
 * @param {string} [props.error] - Error message to display beneath the form, if any.
 * @param {Function} props.handleSubmit - Form submit handler.
 * @returns {JSX.Element}
 */
const CreateWorkspaceForm = ({name, setName, error, handleSubmit}) =>
{
    return (
        <div className="w-full max-w-sm">
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <h1 className="text-2xl font-semibold">Create a new workspace</h1>
                <div className="flex flex-col gap-1.5">
                    <Label htmlFor="name-form">Workspace Name</Label>
                    <Input
                        type="text"
                        name="name"
                        id="name-form"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <SubmitButton buttonText="Create Workspace" />
                {error && (
                    <p className="text-destructive text-sm">{error}</p>
                )}
            </form>
        </div>
    );
};

CreateWorkspaceForm.propTypes = {
    name: PropTypes.string.isRequired,
    setName: PropTypes.func.isRequired,
    error: PropTypes.string,
    handleSubmit: PropTypes.func.isRequired,
};

export default CreateWorkspaceForm;
