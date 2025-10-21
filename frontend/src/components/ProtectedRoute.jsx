import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

const ProtectedRoute = () => {
  const token = localStorage.getItem('accessToken');

  // If there's a token, render the child route (Outlet).
  // Otherwise, redirect to the login page.
  return token ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;