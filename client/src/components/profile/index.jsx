import {useState} from "react";
import Form from "react-bootstrap/Form";
import PropTypes from "prop-types";

import "./index.scss";
import SubmitButton from "../buttons/submitButton";

/**
 * Settings page component with tabbed navigation for account and workspace settings.
 *
 * @param {Object} props
 * @param {Object} props.states - Collection of state values and setters for all form fields.
 * @param {string} props.states.fname - First name field value.
 * @param {Function} props.states.setFname - State setter for first name.
 * @param {string} props.states.lname - Last name field value.
 * @param {Function} props.states.setLname - State setter for last name.
 * @param {string} props.states.email - Email field value.
 * @param {Function} props.states.setEmail - State setter for email.
 * @param {string} props.states.phone - Phone field value.
 * @param {Function} props.states.setPhone - State setter for phone.
 * @param {string} props.states.oldPassword - Current password field value.
 * @param {Function} props.states.setOldPassword - State setter for current password.
 * @param {string} props.states.newPassword - New password field value.
 * @param {Function} props.states.setNewPassword - State setter for new password.
 * @param {string} [props.states.error] - Error message to display, if any.
 * @param {Function} props.handleSubmit - Form submit handler for saving account changes.
 * @returns {JSX.Element}
 */
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
            <div id="nav-container">
                <ul id="settings-nav">
                    <li
                        className={activeTab === "account" ? "active" : ""}
                        onClick={() => setActiveTab("account")}
                    >
                        <h1>Account Settings</h1>
                    </li>
                    <li
                        className={activeTab === "workspace" ? "active" : ""}
                        onClick={() => setActiveTab("workspace")}
                    >
                        <h1>Workspace Settings</h1>
                    </li>
                </ul>
            </div>

            <div id="settings-container">
                <div id="settings-content">
                    {activeTab === "account" ? (
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
