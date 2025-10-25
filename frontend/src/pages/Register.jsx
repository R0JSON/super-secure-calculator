import React, { useState } from 'react';
import { useNavigate, Link, useOutletContext } from 'react-router-dom';
import api from '../api/axiosConfig';
import './Auth.css';

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // THE FIX: Get the whole context object safely
  const context = useOutletContext();
  const setUser = context ? context.setUser : null;

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await api.post('/users/signup', { email, password, full_name: fullName });

      const formData = new URLSearchParams();
      formData.append('username', email);
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
      setError('Registration failed. Email may already be in use.');
      console.error(err);
    }
  };

  return (
    <div className="auth-container">
      <h2>Create Account</h2>
      <form onSubmit={handleRegister} className="auth-form">
        <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full Name" required />
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" required />
        <button type="submit">Register</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      <p className="auth-switch">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  );
}

export default Register;