import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { farmerAPI } from '../../api/farmerAPI';
import { motion, AnimatePresence } from 'framer-motion';
import CropCard from '../../components/common/CropCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import './dashboard.css';

const FarmerDashboard = () => {
  const { user } = useAuth();
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'inventory', 'sold', 'history'
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchMyCrops();
  }, []);

  const fetchMyCrops = async () => {
    try {
      const response = await farmerAPI.getMyCrops();
      setCrops(response.data);
    } catch (error) {
      console.error('Error fetching crops:', error);
      setMessage('Failed to load crops');
    } finally {
      setLoading(false);
    }
  };

  if (loading && crops.length === 0) {
    return <LoadingSpinner />;
  }

  // Analytics calculations
  const stats = {
    total: crops.length,
    available: crops.filter(c => c.status === 'available').length,
    sold: crops.filter(c => c.status === 'sold' || c.status === 'shipped').length,
    delivered: crops.filter(c => c.status === 'delivered').length,
    totalRevenue: crops.reduce((sum, crop) => {
      if (crop.status !== 'available') {
        return sum + (parseFloat(crop.total_price) || 0);
      }
      return sum;
    }, 0)
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>👨‍🌾 Farmer Dashboard</h1>
        <p>Welcome back, {user?.name}</p>
        <motion.button 
          className="btn-action primary"
          onClick={() => window.location.href = '/add-crop'}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          ➕ Add New Crop
        </motion.button>
      </div>

      {message && (
        <motion.div 
          className={`message ${message.includes('success') ? 'success' : 'error'}`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          {message}
        </motion.div>
      )}

      {/* Analytics Section */}
      <motion.div 
        className="analytics-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2>📊 Analytics Overview</h2>
        <div className="stats-grid">
          <motion.div 
            className="stat-card"
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className="stat-icon">📦</div>
            <h3>{stats.total}</h3>
            <p>Total Crops</p>
          </motion.div>

          <motion.div 
            className="stat-card available"
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className="stat-icon">✅</div>
            <h3>{stats.available}</h3>
            <p>Available</p>
          </motion.div>

          <motion.div 
            className="stat-card sold"
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className="stat-icon">🚚</div>
            <h3>{stats.sold}</h3>
            <p>Sold/Shipped</p>
          </motion.div>

          <motion.div 
            className="stat-card delivered"
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className="stat-icon">✔️</div>
            <h3>{stats.delivered}</h3>
            <p>Delivered</p>
          </motion.div>

          <motion.div 
            className="stat-card revenue"
            whileHover={{ scale: 1.05, y: -5 }}
          >
            <div className="stat-icon">💰</div>
            <h3>₹{stats.totalRevenue.toFixed(2)}</h3>
            <p>Total Revenue</p>
          </motion.div>
        </div>
      </motion.div>

      {/* Tab Navigation */}
      <div className="tabs-container">
        <button 
          className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          📦 All Crops ({crops.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => setActiveTab('inventory')}
        >
          ✅ Inventory ({crops.filter(c => c.status === 'available').length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'sold' ? 'active' : ''}`}
          onClick={() => setActiveTab('sold')}
        >
          🚚 Sold ({crops.filter(c => c.status === 'sold' || c.status === 'shipped').length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          ✔️ History ({crops.filter(c => c.status === 'delivered').length})
        </button>
      </div>

      {/* Crops Display Based on Active Tab */}
      <div className="crops-section">
        <AnimatePresence mode="wait">
          {activeTab === 'all' && (
            <motion.div
              key="all"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
              <h2>All Crops</h2>
              {crops.length === 0 ? (
                <div className="empty-state">
                  <p>No crops added yet. Add your first crop to get started!</p>
                </div>
              ) : (
                <div className="crops-grid">
                  {crops.map(crop => (
                    <CropCard key={crop.id} crop={crop} />
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'inventory' && (
            <motion.div
              key="inventory"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
            <h2>Available Inventory</h2>
            {crops.filter(c => c.status === 'available').length === 0 ? (
              <div className="empty-state">
                <p>No crops available in inventory. All crops have been sold.</p>
              </div>
            ) : (
              <div className="crops-grid">
                {crops.filter(c => c.status === 'available').map(crop => (
                  <CropCard key={crop.id} crop={crop} />
                ))}
              </div>
            )}
            </motion.div>
          )}

          {activeTab === 'sold' && (
            <motion.div
              key="sold"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
            <h2>Sold Crops</h2>
            {crops.filter(c => c.status === 'sold' || c.status === 'shipped').length === 0 ? (
              <div className="empty-state">
                <p>No crops in transit. All crops are either available or delivered.</p>
              </div>
            ) : (
              <div className="crops-grid">
                {crops.filter(c => c.status === 'sold' || c.status === 'shipped').map(crop => (
                  <CropCard key={crop.id} crop={crop} />
                ))}
              </div>
            )}
            </motion.div>
          )}

          {activeTab === 'history' && (
            <motion.div
              key="history"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3 }}
            >
            <h2>Completed Deliveries</h2>
            {crops.filter(c => c.status === 'delivered').length === 0 ? (
              <div className="empty-state">
                <p>No completed deliveries yet.</p>
              </div>
            ) : (
              <div className="crops-grid">
                {crops.filter(c => c.status === 'delivered').map(crop => (
                  <CropCard key={crop.id} crop={crop} />
                ))}
              </div>
            )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default FarmerDashboard;