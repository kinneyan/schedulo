import "./index.scss";

import NavigationBar from "../../components/navbar";
import CreateWorkspaceContainer from "../../containers/createWorkspace";
import withAuth from "../../components/auth";

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
