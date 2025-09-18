import { useState, useEffect, useCallback } from "react";
import Cookies from "universal-cookie";
import "./index.scss";

import withAuth from "../../components/auth";
import NavbarContainer from "../../containers/navbar";
import Profile from "../../containers/profile";

const ProfilePage = () => {
    const cookies = new Cookies();
    const token = cookies.get("token");

    // Account settings state
    const [accountData, setAccountData] = useState({
        fname: "",
        lname: "",
        email: "",
        phone: "",
        oldPassword: "",
        newPassword: "",
    });

    const [error, setError] = useState("");
    const [userData, setUserData] = useState(null);
    const [loading, setLoading] = useState(true);

    // Memoized setter for account data
    const updateAccountField = useCallback((field, value) => {
        setAccountData(prev => ({ ...prev, [field]: value }));
    }, []);

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user`, {
                    method: "GET",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${token.access}`,
                    },
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error("Failed to authorize request.");
                    }
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                setUserData(data);

                // Set account form fields
                setAccountData({
                    fname: data.first_name || "",
                    lname: data.last_name || "",
                    email: data.email || "",
                    phone: data.phone || "",
                    oldPassword: "",
                    newPassword: "",
                });
            } catch (error) {
                console.error("Failed to fetch user data:", error);
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        if (token?.access) {
            fetchUserData();
        } else {
            setLoading(false);
        }
    }, [token?.access]);

    const handleAccountSubmit = useCallback(async (e) => {
        e.preventDefault();
        setError("");

        const requestBody = {
            first_name: accountData.fname,
            last_name: accountData.lname,
            email: accountData.email,
            phone: accountData.phone,
        };

        // Only include password fields if user is changing password
        if (accountData.newPassword.trim()) {
            requestBody.current_password = accountData.oldPassword;
            requestBody.password = accountData.newPassword;
        }

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user`, {
                method: "PUT",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token.access}`,
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                const data = await response.json();
                if (response.status === 400 && data.error?.message === "Current password is incorrect.") {
                    throw new Error("Current password is incorrect.");
                }
                throw new Error("Failed to update user information.");
            }

            // Success - reload to get fresh data
            window.location.reload();
        } catch (error) {
            setError(error.message);
        }
    }, [accountData, token?.access]);

    if (loading) {
        return (
            <div id="profile-page">
                <NavbarContainer />
                <div style={{ padding: "2rem", textAlign: "center" }}>Loading...</div>
            </div>
        );
    }

    if (!userData) {
        return (
            <div id="profile-page">
                <NavbarContainer />
                <div style={{ padding: "2rem", textAlign: "center" }}>Failed to load user data</div>
            </div>
        );
    }

    return (
        <div id="profile-page">
            <NavbarContainer />
            <Profile
                accountData={accountData}
                updateAccountField={updateAccountField}
                handleAccountSubmit={handleAccountSubmit}
                userData={userData}
                error={error}
                setError={setError}
            />
        </div>
    );
};

export default withAuth(ProfilePage);
