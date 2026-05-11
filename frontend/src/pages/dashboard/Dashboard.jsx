import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { Navigate } from 'react-router-dom';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const Dashboard = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Redirect to role-specific dashboard
  switch (user.role) {
    case 'farmer':
      return <Navigate to="/farmer-dashboard" replace />;
    case 'retailer':
      return <Navigate to="/retailer-dashboard" replace />;
    case 'distributor':
      return <Navigate to="/distributor-dashboard" replace />;
    case 'customer':
      return <Navigate to="/customer-dashboard" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

export default Dashboard;