import {useState} from "react";
import Cookies from "universal-cookie";
import {Navigate} from "react-router-dom";
import CreateWorkspaceForm from "../../components/forms/createWorkspace";

/**
 * Stateful container that manages workspace creation, including form state and API submission.
 *
 * @returns {JSX.Element}
 */
const CreateWorkspaceContainer = () =>
{
    const [name, setName] = useState("");
    const [error, setError] = useState("");
    const [created, setCreated] = useState(false);

    /**
     * Submits the new workspace name to the API and redirects to the dashboard on success.
     *
     * @param {React.FormEvent<HTMLFormElement>} e - The form submission event.
     * @returns {Promise<void>}
     */
    const handleSubmit = async (e) =>
    {
        e.preventDefault();

        try
        {
            const cookies = new Cookies();
            const token = cookies.get("token");

            const response = await fetch(import.meta.env.VITE_API_URL + "/api/workspace/create/", {
                method: "POST",
                withCredentials: true,
                credentials: "include",
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token.access},
                body: JSON.stringify({name}),
            });

            const data = await response.json();

            if (response.status === 400)
            {
                console.log(data.error.message);
                throw new Error(data.error.message);
            }
            else if (response.status !== 201)
            {
                console.log(response.status);
                throw new Error(response.status);
            }

            setCreated(true);
        }
        catch (error)
        {
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
        </div>
    );
};

export default CreateWorkspaceContainer;
