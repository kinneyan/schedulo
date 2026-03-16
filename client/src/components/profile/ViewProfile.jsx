import PropTypes from "prop-types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import SubmitButton from "../buttons/submitButton/SubmitButton";

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
 * @param {boolean} [props.states.success] - Whether the last save succeeded.
 * @param {Function} props.handleSubmit - Form submit handler for saving account changes.
 * @returns {JSX.Element}
 */
const ViewProfile = ({states, handleSubmit}) =>
{
    const {
        fname, setFname,
        lname, setLname,
        email, setEmail,
        phone, setPhone,
        oldPassword, setOldPassword,
        newPassword, setNewPassword,
        error,
        success,
    } = states;

    return (
        <div className="max-w-2xl mx-auto px-4 py-8">
            <Tabs defaultValue="account">
                <TabsList className="mb-6">
                    <TabsTrigger value="account">Account Settings</TabsTrigger>
                    <TabsTrigger value="workspace">Workspace Settings</TabsTrigger>
                </TabsList>

                <TabsContent value="account">
                    <Card>
                        <CardHeader>
                            <CardTitle>Account Information</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="flex flex-col gap-1.5">
                                        <Label htmlFor="fname">First Name</Label>
                                        <Input id="fname" type="text" value={fname} onChange={(e) => setFname(e.target.value)} />
                                    </div>
                                    <div className="flex flex-col gap-1.5">
                                        <Label htmlFor="lname">Last Name</Label>
                                        <Input id="lname" type="text" value={lname} onChange={(e) => setLname(e.target.value)} />
                                    </div>
                                </div>
                                <div className="flex flex-col gap-1.5">
                                    <Label htmlFor="email">Email</Label>
                                    <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
                                </div>
                                <div className="flex flex-col gap-1.5">
                                    <Label htmlFor="phone">Phone</Label>
                                    <Input id="phone" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
                                </div>

                                <hr className="border-border my-2" />
                                <p className="text-sm font-semibold">Change Password</p>

                                <div className="flex flex-col gap-1.5">
                                    <Label htmlFor="old-password">Current Password</Label>
                                    <Input id="old-password" type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} />
                                </div>
                                <div className="flex flex-col gap-1.5">
                                    <Label htmlFor="new-password">New Password</Label>
                                    <Input id="new-password" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
                                </div>

                                <div className="flex items-center gap-4">
                                    <SubmitButton buttonText="Save" />
                                    {success && <p className="text-sm text-green-700">Changes saved.</p>}
                                </div>
                                {error && <p className="text-destructive text-sm">{error.toString()}</p>}
                            </form>
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="workspace">
                    <Card>
                        <CardHeader>
                            <CardTitle>Workspace Settings</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground text-sm">Workspace settings will be implemented later.</p>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
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
        success: PropTypes.bool,
    }).isRequired,
    handleSubmit: PropTypes.func.isRequired,
};

export default ViewProfile;
