import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { customerAPI } from '../../api/customerAPI';
import CropCard from '../../components/common/CropCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import './dashboard.css';

const CustomerDashboard = () => {
  const { user } = useAuth();
  const [availableCrops, setAvailableCrops] = useState([]);
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
      const [cropsResponse, purchasesResponse] = await Promise.all([
        customerAPI.getAvailableCrops(),
        customerAPI.getMyPurchases()
      ]);

      setAvailableCrops(cropsResponse.data);
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
      await customerAPI.buyCrop(cropId, quantity);
      setMessage('Product purchased successfully!');
      fetchData(); // Refresh all data
    } catch (error) {
      console.error('Error buying product:', error);
      setMessage(error.response?.data?.error || 'Failed to purchase product');
    } finally {
      setLoading(false);
    }
  };

  if (loading && availableCrops.length === 0 && purchases.length === 0) {
    return <LoadingSpinner />;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>🏪 Customer Dashboard</h1>
        <p>Welcome back, {user?.name}</p>
      </div>

      {message && (
        <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'available' ? 'active' : ''}`}
          onClick={() => setActiveTab('available')}
        >
          Available Products ({availableCrops.length})
        </button>
        <button 
          className={`tab ${activeTab === 'purchases' ? 'active' : ''}`}
          onClick={() => setActiveTab('purchases')}
        >
          My Orders ({purchases.length})
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'available' && (
          <div>
            <h2>Products Available from Distributors</h2>
            {availableCrops.length === 0 ? (
              <div className="empty-state">
                <p>No products available from distributors at the moment.</p>
              </div>
            ) : (
              <div className="crops-grid">
                {availableCrops.map(crop => (
                  <CropCard 
                    key={crop.id} 
                    crop={crop}
                    onBuy={handleBuyCrop}
                    showBuyButton={true}
                    userRole="customer"
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'purchases' && (
          <div>
            <h2>My Purchase History</h2>
            {purchases.length === 0 ? (
              <div className="empty-state">
                <p>No purchases made yet. Start shopping to see your orders here!</p>
              </div>
            ) : (
              <div className="purchases-list">
                {purchases.map(purchase => (
                  <div key={purchase.id} className="purchase-item">
                    <div className="purchase-info">
                      <h4>{purchase.crop_name}</h4>
                      <p>From Distributor: {purchase.distributor_name}</p>
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

export default CustomerDashboard;