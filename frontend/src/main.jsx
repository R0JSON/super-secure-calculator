import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import App from './App.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Posts from './pages/Posts.jsx'; // Add this import
import PostsPage from './pages/PostPage.jsx'; // Add this import
import ProtectedRoute from './components/ProtectedRoute.jsx';

import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/*
          This is a "Layout Route". The App component will now render for
          all child routes, and it will contain the <Outlet />.
          Because it's rendered by a Route, it now has router context.
        */}
        <Route element={<App />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
              path="/posts-public"
              element={
                <ProtectedRoute>
                  <PostsPage />
                </ProtectedRoute>
              }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/posts"
            element={
              <ProtectedRoute>
                <Posts />
              </ProtectedRoute>
            }
          />
          {/* Add a default route to redirect users */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);