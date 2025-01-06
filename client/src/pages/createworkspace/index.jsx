import React from 'react';
import './index.scss';

import NavigationBar from '../../components/navbar';
import CreateWorkspaceContainer from '../../containers/createworkspace';

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

export default CreateWorkspacePage;
