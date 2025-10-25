import React, { useState } from 'react';
import { useNavigate, Link, useOutletContext } from 'react-router-dom';
import api from '../api/axiosConfig';
import './Auth.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // THE FIX: Get the whole context object safely
  const context = useOutletContext();
  const setUser = context ? context.setUser : null;

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/login/access-token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      localStorage.setItem('accessToken', response.data.access_token);

      const userResponse = await api.get('/users/me');

      // Use the setUser function only if it exists
      if (setUser) {
        setUser(userResponse.data);
      }

      navigate('/dashboard');
    } catch (err) {
      setError('Login failed. Please check your credentials.');
      console.error(err);
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin} className="auth-form">
        <input type="email" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Email" required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      <p className="auth-switch">
        Need an account? <Link to="/register">Sign Up</Link>
      </p>
    </div>
  );
}

export default Login;