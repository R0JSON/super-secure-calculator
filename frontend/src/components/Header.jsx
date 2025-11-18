import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import './Header.css';
function Header({ user, handleLogout }) {
const loggedOutLinks = (
<>
<li>
<NavLink to="/login">Login</NavLink>
</li>
<li>
<NavLink to="/register">Register</NavLink>
</li>
</>
);
const loggedInLinks = (
<>
<li className="user-welcome">
<span>Welcome, {user?.full_name || user?.email}!</span>
</li>
<li>
<button onClick={handleLogout} className="logout-button-header">
Logout
</button>
</li>
</>
);
return (
<header className="app-header">
<nav className="app-nav">
<Link to="/" className="nav-brand">
SecureCalc
</Link>
<ul className="nav-links">
{user ? loggedInLinks : loggedOutLinks}
</ul>
</nav>
</header>
);
}
export default Header;