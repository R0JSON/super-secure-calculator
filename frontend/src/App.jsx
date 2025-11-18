import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import api from './api/axiosConfig';
import Header from './components/Header'; // Import the new Header
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  // On initial load, check for a token and fetch user data
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      const fetchUser = async () => {
        try {
          // NOTE: Your axios config likely prefixes this with /api/v1
          const response = await api.get('/users/me');
          setUser(response.data);
        } catch (error) {
          // Token is invalid or expired, clear it
          localStorage.removeItem('accessToken');
        }
      };
      fetchUser();
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    setUser(null);
    navigate('/login');
  };

  return (
    <>
      <Header user={user} handleLogout={handleLogout} />
      <main className="app-content">
        {/* Pass user state and setters to all child routes */}
        <Outlet context={{ user, setUser }} />
      </main>
    </>
  );
}

export default App;