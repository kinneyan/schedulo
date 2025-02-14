import React from 'react';
import Form from 'react-bootstrap/Form';

const ViewProfile = () => {
    return (
        <div>
            <div>
                <h1>Settings</h1>
                <ul>
                    <li onClick={PageSwitcher}>Account</li>
                    <li onClick={PageSwitcher}>Workspaces</li>
                </ul>
            </div>
            <div id="account-settings-container">
                <h1>Account Settings</h1>
                <Form>
                    <Form.Label>Name</Form.Label>
                    <Form.Group>
                        <Form.Label>First name</Form.Label>
                        <Form.Control type="text" placeholder="First name"/>
                    </Form.Group>
                    <Form.Group>
                        <Form.Label>Last name</Form.Label>
                        <Form.Control type="text" placeholder="Last name"/>
                    </Form.Group>
                </Form>
                <Form>
                    <Form.Label>Contact Information</Form.Label>
                    <Form.Group>
                        <Form.Label>Email</Form.Label>
                        <Form.Control type="email" placeholder="Email" />
                    </Form.Group>
                    <Form.Group>
                        <Form.Label>Phone</Form.Label>
                        <Form.Control type="phone" placeholder="999-999-9999" />
                    </Form.Group>
                </Form>
                <Form>
                    <Form.Label>Update Password</Form.Label>
                    <Form.Group>
                        <Form.Label>Old Password</Form.Label>
                        <Form.Control type="password" placeholder="Old password" />
                    </Form.Group>
                    <Form.Group>
                        <Form.Label>New Password</Form.Label>
                        <Form.Control type="password" placeholder="New password" />
                    </Form.Group>
                </Form>
            </div>
        </div>
    );
};

const PageSwitcher = () => {

};

export default ViewProfile;
