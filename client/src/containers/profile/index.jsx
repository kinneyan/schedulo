import PropTypes from "prop-types";
import ViewProfile from "../../components/profile";

const Profile = ({
    accountData,
    updateAccountField,
    handleAccountSubmit,
    userData,
    error,
    setError,
}) => {
    // Transform accountData into legacy states format for ViewProfile
    const states = {
        fname: accountData.fname,
        setFname: (value) => updateAccountField("fname", value),
        lname: accountData.lname,
        setLname: (value) => updateAccountField("lname", value),
        email: accountData.email,
        setEmail: (value) => updateAccountField("email", value),
        phone: accountData.phone,
        setPhone: (value) => updateAccountField("phone", value),
        oldPassword: accountData.oldPassword,
        setOldPassword: (value) => updateAccountField("oldPassword", value),
        newPassword: accountData.newPassword,
        setNewPassword: (value) => updateAccountField("newPassword", value),
        error,
        setError,
    };

    return (
        <div>
            <ViewProfile
                states={states}
                handleSubmit={handleAccountSubmit}
                userData={userData}
            />
        </div>
    );
};

Profile.propTypes = {
    accountData: PropTypes.shape({
        fname: PropTypes.string.isRequired,
        lname: PropTypes.string.isRequired,
        email: PropTypes.string.isRequired,
        phone: PropTypes.string.isRequired,
        oldPassword: PropTypes.string.isRequired,
        newPassword: PropTypes.string.isRequired,
    }).isRequired,
    updateAccountField: PropTypes.func.isRequired,
    handleAccountSubmit: PropTypes.func.isRequired,
    userData: PropTypes.object.isRequired,
    error: PropTypes.string.isRequired,
    setError: PropTypes.func.isRequired,
};

export default Profile;
