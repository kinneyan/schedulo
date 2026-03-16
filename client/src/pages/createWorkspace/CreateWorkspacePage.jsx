import NavbarContainer from "../../containers/navbar/NavbarContainer";
import CreateWorkspaceContainer from "../../containers/createWorkspace/CreateWorkspaceContainer";

/**
 * Authenticated page for creating a new workspace.
 *
 * @returns {JSX.Element}
 */
const CreateWorkspacePage = () =>
{
    return (
        <div>
            <NavbarContainer />
            <div className="flex justify-center pt-16 px-4">
                <CreateWorkspaceContainer />
            </div>
        </div>
    );
};

export default CreateWorkspacePage;
