import "./index.scss";

import NavigationBar from "../../components/navbar/NavigationBar";
import CreateWorkspaceContainer from "../../containers/createWorkspace/CreateWorkspaceContainer";
import withAuth from "../../components/auth/WithAuth";

/**
 * Page that renders the workspace creation form, protected by authentication.
 *
 * @returns {JSX.Element}
 */
const CreateWorkspacePage = () =>
{
    return (
        <div id="create-workspace-page">
            <NavigationBar />
            <div id="create-workspace-form-container">
                <CreateWorkspaceContainer />
            </div>
        </div>
    );
};

export default withAuth(CreateWorkspacePage);
