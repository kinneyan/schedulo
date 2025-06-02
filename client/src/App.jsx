import { BrowserRouter, Routes, Route } from 'react-router-dom';

import HomePage from './pages/home';
import LoginPage from './pages/login';
import ProfilePage from './pages/profile';
import DashboardPage from './pages/dashboard';
import RegisterPage from './pages/register';
import CreateWorkspacePage from './pages/createworkspace';

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
};

export default App;
