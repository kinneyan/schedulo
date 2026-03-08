import {BrowserRouter, Routes, Route} from "react-router-dom";

import HomePage from "./pages/home/HomePage";
import LoginPage from "./pages/login/LoginPage";
import ProfilePage from "./pages/profile/ProfilePage";
import DashboardPage from "./pages/dashboard/DashboardPage";
import RegisterPage from "./pages/register/RegisterPage";
import CreateWorkspacePage from "./pages/createWorkspace/CreateWorkspacePage";

/**
 * Root application component that defines the client-side route tree.
 *
 * @returns {JSX.Element}
 */
function App()
{
    return (
        <>
            <BrowserRouter>
                <Routes>
                    <Route index element={<HomePage />} />
                    <Route path="login" element={<LoginPage />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="profile" element={<ProfilePage />} />
                    <Route path="register" element={<RegisterPage />} />
                    <Route path="create-workspace" element={<CreateWorkspacePage />} />
                </Routes>
            </BrowserRouter>
        </>
    );
}

export default App;
