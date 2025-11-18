import React from 'react';
import { Navigate, useOutletContext, useLocation } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  // Get the user state from the parent App component
  const context = useOutletContext();
  const user = context ? context.user : null;
  const location = useLocation();

  // Check for the token in localStorage as the primary guard
  const token = localStorage.getItem('accessToken');

  // Case 1: No token exists. Redirect to login immediately.
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Case 2: A token exists, but the user object hasn't been loaded into state yet.
  // This is the crucial "waiting" state that solves the race condition.
  // App.jsx is currently busy fetching the user data.
  if (token && !user) {
    // You can replace this with a fancy spinner component
    return <div>Verifying session...</div>;
  }

  // Case 3: A token exists AND we have the user object in our state.
  // The user is fully authenticated. Render the requested component (the Dashboard).
  return children;
};

export default ProtectedRoute;