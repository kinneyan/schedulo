import React, {useState} from 'react';

import ViewProfile from '../../components/profile';

const Profile = () => 
{
    const [fname, setFname] = useState("");
    const [lname, setLname] = useState("");
    const [email, setEmail] = useState("");
    const [phone, setPhone] = useState("");
    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const states = {
        fname,
        setFname,
        lname,
        setLname,
        email,
        setEmail,
        phone,
        setPhone,
        oldPassword,
        setOldPassword,
        newPassword,
        setNewPassword
    }

    return (
        <div>
            <ViewProfile states={states}/>
        </div>
    );
};

export default Profile;
