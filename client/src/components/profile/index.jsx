import {useState} from "react";
import Form from "react-bootstrap/Form";
import PropTypes from "prop-types";

import "./index.scss";
import SubmitButton from "../buttons/submitButton";

const ViewProfile = ({states, handleSubmit}) => 
{
    const [activeTab, setActiveTab] = useState("account");

    const {
        fname, setFname,
        lname, setLname,
        email, setEmail,
        phone, setPhone,
        oldPassword, setOldPassword,
        newPassword, setNewPassword,
        error,
    } = states;
    
    return (
        <div id="settings-component">
            <div id="settings-container">
                <div id="nav-container">
                    <ul id="settings-nav">
                        <li 
                            className={activeTab === "account" ? "active" : ""} 
                            onClick={() => setActiveTab("account")}
                        >
                            <span>Account Settings</span>
                        </li>
                        <li 
                            className={activeTab === "workspace" ? "active" : ""} 
                            onClick={() => setActiveTab("workspace")}
                        >
                            <span>Workspace Settings</span>
                        </li>
                    </ul>
                </div>

                <div id="settings-content">
                    {activeTab === "account" ? (
                        <div className="settings-form-container">
                            <h3>Account Information</h3>
                            <Form onSubmit={handleSubmit}>
                                <Form.Group className="fgroup">
                                    <Form.Label>First Name</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        value={fname} 
                                        onChange={(e) => setFname(e.target.value)} 
                                    />
                                </Form.Group>

                                <Form.Group className="fgroup">
                                    <Form.Label>Last Name</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        value={lname} 
                                        onChange={(e) => setLname(e.target.value)} 
                                    />
                                </Form.Group>

                                <Form.Group className="fgroup">
                                    <Form.Label>Email</Form.Label>
                                    <Form.Control 
                                        type="email" 
                                        value={email} 
                                        onChange={(e) => setEmail(e.target.value)} 
                                    />
                                </Form.Group>

                                <Form.Group className="fgroup">
                                    <Form.Label>Phone</Form.Label>
                                    <Form.Control 
                                        type="tel" 
                                        value={phone} 
                                        onChange={(e) => setPhone(e.target.value)} 
                                    />
                                </Form.Group>

                                <h3>Change Password</h3>
                                
                                <Form.Group className="fgroup">
                                    <Form.Label>Current Password</Form.Label>
                                    <Form.Control 
                                        type="password" 
                                        value={oldPassword} 
                                        onChange={(e) => setOldPassword(e.target.value)} 
                                    />
                                </Form.Group>

                                <Form.Group className="fgroup">
                                    <Form.Label>New Password</Form.Label>
                                    <Form.Control 
                                        type="password" 
                                        value={newPassword} 
                                        onChange={(e) => setNewPassword(e.target.value)} 
                                    />
                                </Form.Group>

                                <div id="button-item">
                                    <SubmitButton buttonText="Save" onClick={handleSubmit} />
                                </div>
                            </Form>
                        </div>
                    ) : (
                        <div className="settings-form-container">
                            <h3>Workspace Settings</h3>
                            <p>Workspace settings will be implemented later.</p>
                        </div>
                    )}
                </div>
            </div>
            {error && <div id="error-container"><p id="error-text">{error.toString()}</p></div>}
        </div>
    );
};

ViewProfile.propTypes = {
    states: PropTypes.shape({
        fname: PropTypes.string.isRequired,
        setFname: PropTypes.func.isRequired,
        lname: PropTypes.string.isRequired,
        setLname: PropTypes.func.isRequired,
        email: PropTypes.string.isRequired,
        setEmail: PropTypes.func.isRequired,
        phone: PropTypes.string.isRequired,
        setPhone: PropTypes.func.isRequired,
        oldPassword: PropTypes.string.isRequired,
        setOldPassword: PropTypes.func.isRequired,
        newPassword: PropTypes.string.isRequired,
        setNewPassword: PropTypes.func.isRequired,
        error: PropTypes.string,
    }).isRequired,
    handleSubmit: PropTypes.func.isRequired,
};

export default ViewProfile;
