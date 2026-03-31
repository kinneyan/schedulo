import {BrowserRouter, Routes, Route, Navigate} from "react-router-dom";
import Cookies from "universal-cookie";

import LoginPage from "./pages/login/LoginPage";
import ProfilePage from "./pages/profile/ProfilePage";
import DashboardPage from "./pages/dashboard/DashboardPage";
import RegisterPage from "./pages/register/RegisterPage";
import CreateWorkspacePage from "./pages/createWorkspace/CreateWorkspacePage";
import NotFoundPage from "./pages/notFound/NotFoundPage";
import ProtectedRoute from "./components/auth/ProtectedRoute";

/**
 * Redirects to /dashboard if a token cookie exists, otherwise to /login.
 *
 * @returns {JSX.Element}
 */
const RootRedirect = () =>
{
    const cookies = new Cookies();
    const token = cookies.get("token");
    return token ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />;
};

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
                    <Route index element={<RootRedirect />} />
                    <Route path="login" element={<LoginPage />} />
                    <Route path="register" element={<RegisterPage />} />
                    <Route element={<ProtectedRoute />}>
                        <Route path="dashboard" element={<DashboardPage />} />
                        <Route path="profile" element={<ProfilePage />} />
                        <Route path="create-workspace" element={<CreateWorkspacePage />} />
                    </Route>
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            </BrowserRouter>
        </>
    );
}

export default App;
