import { BrowserRouter, Routes, Route } from 'react-router-dom';

import HomePage from './pages/home';
import LoginPage from './pages/login';
import ProfilePage from './pages/profile';
import DashboardPage from './pages/dashboard';

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
        </Routes>
      </BrowserRouter>
    </>
  );
};

export default App
