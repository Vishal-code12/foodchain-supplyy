import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { retailerAPI } from '../../api/retailerAPI';
import CropCard from '../../components/common/CropCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import './dashboard.css';

const RetailerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [availableCrops, setAvailableCrops] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [purchases, setPurchases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('available');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cropsResponse, inventoryResponse, purchasesResponse] = await Promise.all([
        retailerAPI.getAvailableCrops(),
        retailerAPI.getInventory(),
        retailerAPI.getMyPurchases()
      ]);

      setAvailableCrops(cropsResponse.data);
      setInventory(inventoryResponse.data);
      setPurchases(purchasesResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setMessage('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleBuyCrop = async (cropId, quantity = 1) => {
    try {
      setLoading(true);
      await retailerAPI.buyCrop(cropId, quantity);
      setMessage('Crop purchased successfully!');
      fetchData(); // Refresh all data
    } catch (error) {
      console.error('Error buying crop:', error);
      setMessage(error.response?.data?.error || 'Failed to purchase crop');
    } finally {
      setLoading(false);
    }
  };

  if (loading && availableCrops.length === 0) {
    return <LoadingSpinner />;
  }

  // Analytics calculations
  const stats = {
    availableCount: availableCrops.length,
    inventoryCount: inventory.length,
    purchasesCount: purchases.length,
    totalValue: inventory.reduce((sum, item) => sum + (parseFloat(item.total_price) || 0), 0)
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>🛒 Retailer Dashboard</h1>
        <p>Welcome back, {user?.name}</p>
        <button 
          className="btn-action primary"
          onClick={() => window.location.href = '/buy-crop'}
        >
          🛍️ Buy Crops
        </button>
      </div>

      {message && (
        <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      {/* Analytics Section */}
      <div className="analytics-section">
        <h2>📊 Analytics Overview</h2>
        <div className="stats-grid">
          <div 
            className="stat-card available clickable" 
            onClick={() => navigate('/buy-crop')}
            title="Click to buy crops"
          >
            <div className="stat-icon">🌾</div>
            <h3>{stats.availableCount}</h3>
            <p>Available to Buy</p>
            <span className="click-hint">👆 Click to browse</span>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📦</div>
            <h3>{stats.inventoryCount}</h3>
            <p>My Inventory</p>
          </div>

          <div className="stat-card sold">
            <div className="stat-icon">🛒</div>
            <h3>{stats.purchasesCount}</h3>
            <p>Total Purchases</p>
          </div>

          <div className="stat-card revenue">
            <div className="stat-icon">💰</div>
            <h3>₹{stats.totalValue.toFixed(2)}</h3>
            <p>Inventory Value</p>
          </div>
        </div>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'available' ? 'active' : ''}`}
          onClick={() => setActiveTab('available')}
        >
          Available Crops ({availableCrops.length})
        </button>
        <button 
          className={`tab ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => setActiveTab('inventory')}
        >
          My Inventory ({inventory.length})
        </button>
        <button 
          className={`tab ${activeTab === 'purchases' ? 'active' : ''}`}
          onClick={() => setActiveTab('purchases')}
        >
          Purchase History ({purchases.length})
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'available' && (
          <div>
            <div className="section-header">
              <h2>Crops Available from Farmers</h2>
              <button 
                className="btn-view-all"
                onClick={() => navigate('/buy-crop')}
              >
                View All & Buy →
              </button>
            </div>
            {availableCrops.length === 0 ? (
              <div className="empty-state">
                <p>No crops available from farmers at the moment.</p>
              </div>
            ) : (
              <div className="crops-grid">
                {availableCrops.slice(0, 3).map(crop => (
                  <div 
                    key={crop.id}
                    onClick={() => navigate('/buy-crop')}
                    className="crop-card-wrapper"
                    title="Click to buy crops"
                  >
                    <CropCard 
                      crop={crop}
                      userRole="retailer"
                    />
                    <div className="click-overlay">
                      <span>🛍️ Click to Buy</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {availableCrops.length > 3 && (
              <div className="view-more">
                <button 
                  className="btn-secondary"
                  onClick={() => navigate('/buy-crop')}
                >
                  View All {availableCrops.length} Crops →
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'inventory' && (
          <div>
            <h2>My Inventory</h2>
            {inventory.length === 0 ? (
              <div className="empty-state">
                <p>No crops in inventory. Purchase some crops to get started!</p>
              </div>
            ) : (
              <div className="crops-grid">
                {inventory.map(crop => (
                  <CropCard key={crop.id} crop={crop} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'purchases' && (
          <div>
            <h2>Purchase History</h2>
            {purchases.length === 0 ? (
              <div className="empty-state">
                <p>No purchases made yet.</p>
              </div>
            ) : (
              <div className="purchases-list">
                {purchases.map(purchase => (
                  <div key={purchase.id} className="purchase-item">
                    <div className="purchase-info">
                      <h4>{purchase.crop_name}</h4>
                      <p>From: {purchase.farmer_name}</p>
                      <p>Quantity: {purchase.quantity}</p>
                      <p>Total: ₹{purchase.price}</p>
                      <p>Date: {new Date(purchase.timestamp).toLocaleDateString()}</p>
                    </div>
                    {purchase.image_path && (
                      <img 
                        src={`http://localhost:5000/static/uploads/${purchase.image_path}`}
                        alt={purchase.crop_name}
                        className="purchase-image"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RetailerDashboard;