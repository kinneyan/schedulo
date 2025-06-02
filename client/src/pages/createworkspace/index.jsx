import React from 'react';
import './index.scss';

import NavigationBar from '../../components/navbar';
import CreateWorkspaceContainer from '../../containers/createworkspace';
import with_auth from '../../components/auth';

const CreateWorkspacePage = () => {
    return (
        <div id="create-workspace-page">
            <NavigationBar />
            <div id="create-workspace-form-container">
                <CreateWorkspaceContainer />
            </div>
        </div>
    );
};

export default with_auth(CreateWorkspacePage);
