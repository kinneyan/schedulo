import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import HomePage from './pages/home';
import LoginPage from './pages/login';

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route index element={<HomePage />} />
          <Route path="login" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </>
  );
};

export default App
