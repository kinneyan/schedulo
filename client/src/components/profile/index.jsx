import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';

import './index.scss';
import '../submitbutton'
import SubmitButton from '../submitbutton';

const ViewProfile = ({states, handleSubmit}) => {
  const [activeTab, setActiveTab] = useState('account'); // Default to account tab

  const {
    fname, setFname,
    lname, setLname,
    email, setEmail,
    phone, setPhone,
    oldPassword, setOldPassword,
    newPassword, setNewPassword,
    error, setError,
  } = states;
  
  return (
    <div id="settings-component">
      <div id="nav-container">
        <ul id="settings-nav">
          <li 
            className={activeTab === 'account' ? 'active' : ''} 
            onClick={() => setActiveTab('account')}
          >
            <h1>Account Settings</h1>
          </li>
          <li 
            className={activeTab === 'workspace' ? 'active' : ''} 
            onClick={() => setActiveTab('workspace')}
          >
            <h1>Workspace Settings</h1>
          </li>
        </ul>
      </div>

      <div id="settings-container">
        <div id="settings-content">
          {activeTab === 'account' ? (
            <div className="settings-form-container">
              <h3>Account Information</h3>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="fgroup">
                  <h4>First Name</h4>
                  <Form.Control 
                    type="text" 
                    value={fname} 
                    onChange={(e) => setFname(e.target.value)} 
                  />
                </Form.Group>

                <Form.Group className="fgroup">
                  <h4>Last Name</h4>
                  <Form.Control 
                    type="text" 
                    value={lname} 
                    onChange={(e) => setLname(e.target.value)} 
                  />
                </Form.Group>

                <Form.Group className="fgroup">
                  <h4>Email</h4>
                  <Form.Control 
                    type="email" 
                    value={email} 
                    onChange={(e) => setEmail(e.target.value)} 
                  />
                </Form.Group>

                <Form.Group className="fgroup">
                  <h4>Phone</h4>
                  <Form.Control 
                    type="tel" 
                    value={phone} 
                    onChange={(e) => setPhone(e.target.value)} 
                  />
                </Form.Group>

                <h3>Change Password</h3>
                
                <Form.Group className="fgroup">
                  <h4>Current Password</h4>
                  <Form.Control 
                    type="password" 
                    value={oldPassword} 
                    onChange={(e) => setOldPassword(e.target.value)} 
                  />
                </Form.Group>

                <Form.Group className="fgroup">
                  <h4>New Password</h4>
                  <Form.Control 
                    type="password" 
                    value={newPassword} 
                    onChange={(e) => setNewPassword(e.target.value)} 
                  />
                </Form.Group>

                <div id="button-item">
                  <SubmitButton button_text="Save" onClick={handleSubmit} />
                </div>
              </Form>
            </div>
          ) : (
            <div className="settings-form-container">
              <h3>Workspace Settings</h3>
              {/* Workspace settings content will be added later */}
              <p>Workspace settings will be implemented later.</p>
            </div>
          )}
        </div>
      </div>
      { error && <div id="error-container"><p id="error-text">{error.toString()}</p></div> }
    </div>
  );
};

export default ViewProfile;
