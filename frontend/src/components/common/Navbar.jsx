import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDashboardPath = () => {
    if (!user) return '/dashboard';
    return `/${user.role}-dashboard`;
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🌱 FoodChain Supply</Link>
      </div>
      
      <div className="navbar-menu">
        {isAuthenticated ? (
          <>
            <Link to="/" className="navbar-item">
              🏠 Home
            </Link>
            <Link to={getDashboardPath()} className="navbar-item">
              📊 Dashboard
            </Link>
            <Link to="/trace" className="navbar-item">
              🔍 Trace Product
            </Link>
            <div className="navbar-user">
              <span>Welcome, {user?.name} ({user?.role})</span>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <Link to="/" className="navbar-item">
              🏠 Home
            </Link>
            <Link to="/login" className="navbar-item">
              Login
            </Link>
            <Link to="/register" className="navbar-item">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;