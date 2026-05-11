import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { MetaMaskProvider } from './context/MetaMaskContext';
import Navbar from './components/common/Navbar';
import ProtectedRoute from './components/common/ProtectedRoute';

// Pages
import Home from './pages/Home';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import MetaMaskLogin from './components/auth/MetaMaskLogin';
import Dashboard from './pages/dashboard/Dashboard';
import FarmerDashboard from './pages/dashboard/FarmerDashboard';
import RetailerDashboard from './pages/dashboard/RetailerDashboard';
import DistributorDashboard from './pages/dashboard/DistributorDashboard';
import CustomerDashboard from './pages/dashboard/CustomerDashboard';
import ProductTrace from './pages/trace/ProductTrace';

// Action Pages
import AddCrop from './pages/actions/AddCrop';
import BuyCrop from './pages/actions/BuyCrop';
import BuyFromRetailer from './pages/actions/BuyFromRetailer';

import './App.css';

function App() {
  return (
    <MetaMaskProvider>
      <AuthProvider>
        <Router>
        <div className="App">
          <Navbar />
          <main className="main-content">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/metamask-login" element={<MetaMaskLogin />} />
              <Route path="/trace" element={<ProductTrace />} />

              {/* Protected routes */}
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />

              <Route path="/farmer-dashboard" element={
                <ProtectedRoute requiredRole="farmer">
                  <FarmerDashboard />
                </ProtectedRoute>
              } />

              <Route path="/retailer-dashboard" element={
                <ProtectedRoute requiredRole="retailer">
                  <RetailerDashboard />
                </ProtectedRoute>
              } />

              <Route path="/distributor-dashboard" element={
                <ProtectedRoute requiredRole="distributor">
                  <DistributorDashboard />
                </ProtectedRoute>
              } />

              <Route path="/customer-dashboard" element={
                <ProtectedRoute requiredRole="customer">
                  <CustomerDashboard />
                </ProtectedRoute>
              } />

              {/* Action routes */}
              <Route path="/add-crop" element={
                <ProtectedRoute requiredRole="farmer">
                  <AddCrop />
                </ProtectedRoute>
              } />

              <Route path="/buy-crop" element={
                <ProtectedRoute requiredRole="retailer">
                  <BuyCrop />
                </ProtectedRoute>
              } />

              <Route path="/buy-from-retailer" element={
                <ProtectedRoute requiredRole="distributor">
                  <BuyFromRetailer />
                </ProtectedRoute>
              } />

              {/* Catch all route */}
              <Route path="*" element={<Home />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
    </MetaMaskProvider>
  );
}

export default App;