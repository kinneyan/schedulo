import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';

import './index.scss';
import '../submitbutton'
import SubmitButton from '../submitbutton';

const ViewProfile = () => 
{
    const Pages = 
    {
        ACCOUNT: "account",
        WORKSPACES: "workspaces"
    }
    
    const [page, setPage] = useState(Pages.ACCOUNT);

    const Settings = () =>
    {
        const AccountSettings = () => 
        {
            return (
                <div>
                    <Form>
                        <Form.Label><h4>Name</h4></Form.Label>
                        <Form.Group className="fgroup">
                            <Form.Label>First name</Form.Label>
                            <Form.Control type="text" placeholder="John"/>
                        </Form.Group>
                        <Form.Group className="fgroup">
                            <Form.Label>Last name</Form.Label>
                            <Form.Control type="text" placeholder="Doe"/>
                        </Form.Group>
                    </Form>
                    <Form>
                        <Form.Label><h4>Contact Information</h4></Form.Label>
                        <Form.Group className="fgroup">
                            <Form.Label>Email</Form.Label>
                            <Form.Control type="email" placeholder="yourname@example.com" />
                        </Form.Group>
                        <Form.Group className="fgroup">
                            <Form.Label>Phone</Form.Label>
                            <Form.Control type="phone" placeholder="999-999-9999" />
                        </Form.Group>
                    </Form>
                    <Form>
                        <Form.Label><h4>Update Password</h4></Form.Label>
                        <Form.Group className="fgroup">
                            <Form.Label>Current Password</Form.Label>
                            <Form.Control type="password" />
                        </Form.Group>
                        <Form.Group className="fgroup">
                            <Form.Label>New Password</Form.Label>
                            <Form.Control type="password" />
                        </Form.Group>
                    </Form>
                </div>
            );
        }

        const WorkspaceSettings = () =>
        {
            return (
                <div>
                </div>
            );
        }

        if (page === Pages.ACCOUNT)
        {
            return (
                <div class="settings-form-container">
                    <h3>Account Settings</h3>
                    <AccountSettings />
                </div>
            );
        }
        else if (page === Pages.WORKSPACES)
        {
            return (
                <div class="settings-form-container">
                    <h3>Workspace Settings</h3>
                    <WorkspaceSettings />
                </div>
            );
        }
    };

    return (
        <div id="settings-component">
            <div id="nav-container">
                <ul id="settings-nav">
                    <li onClick={() => setPage(Pages.ACCOUNT)}><h1>Account</h1></li>
                    <li onClick={() => setPage(Pages.WORKSPACES)}><h1>Workspaces</h1></li>
                </ul>
            </div>
            <div id="settings-container">
                <div id="settings-content">
                    <Settings />
                    <SubmitButton button_text="Save" />
                </div>
            </div>
        </div>
    );
};

export default ViewProfile;
