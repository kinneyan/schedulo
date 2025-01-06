import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import HomePage from './pages/home';
import LoginPage from './pages/login';
import RegisterPage from './pages/register';
import CreateWorkspacePage from './pages/createworkspace';

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
          <Route path="dashboard" element={<HomePage />} />
          <Route path="create-workspace" element={<CreateWorkspacePage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
};

export default App
