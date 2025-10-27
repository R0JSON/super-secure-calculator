import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import api from './api/axiosConfig';
import Header from './components/Header';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // On initial load, check for a token and fetch user data
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      const fetchUser = async () => {
        try {
          const response = await api.get('/users/me');
          setUser(response.data);
        } catch (error) {
          console.error('Error fetching user:', error);
          // Token is invalid or expired, clear it
          localStorage.removeItem('accessToken');
        } finally {
          setLoading(false);
        }
      };
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    setUser(null);
    navigate('/login');
  };

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

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