import React from 'react';
import { useOutletContext } from 'react-router-dom';
import Calculator from '../components/Calculator';
import './Dashboard.css';

function Dashboard() {
  // Get the user object from the parent App component's context.
  const context = useOutletContext();

  // Thanks to our new ProtectedRoute, we can be confident that if this
  // component renders, the context and user object will exist.
  // We add a failsafe check just in case.
  if (!context || !context.user) {
    // This should theoretically never be seen by the user.
    return <div>Loading...</div>;
  }

  // The main dashboard UI, now clean and simple.
  return (
    <div className="dashboard-container">
      <main className="dashboard-content">
        <Calculator />
      </main>
    </div>
  );
}

export default Dashboard;