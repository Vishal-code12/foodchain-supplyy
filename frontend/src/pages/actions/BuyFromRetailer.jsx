import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { distributorAPI } from '../../api/distributorAPI';
import CropCard from '../../components/common/CropCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import './actions.css';

const BuyFromRetailer = () => {
  const navigate = useNavigate();
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [purchaseQuantity, setPurchaseQuantity] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchAvailableCrops();
  }, []);

  const fetchAvailableCrops = async () => {
    try {
      const response = await distributorAPI.getAvailableCrops();
      setCrops(response.data);
    } catch (error) {
      console.error('Error fetching crops:', error);
      setMessage('Failed to load available crops');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (e) => {
    e.preventDefault();
    if (!selectedCrop) return;

    setLoading(true);
    try {
      await distributorAPI.buyCrop(selectedCrop.id, parseFloat(purchaseQuantity));

      setMessage('Purchase successful!');
      setTimeout(() => {
        navigate('/distributor-dashboard');
      }, 1500);
    } catch (error) {
      console.error('Error purchasing crop:', error);
      setMessage(error.response?.data?.error || 'Failed to purchase crop');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="action-page">
      <motion.div 
        className="action-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="action-header">
          <h1>🚚 Buy from Retailers</h1>
          <button onClick={() => navigate('/distributor-dashboard')} className="btn-back">
            ← Back to Dashboard
          </button>
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

        {!selectedCrop ? (
          <div className="crops-grid">
            <h2>Available Products from Retailers</h2>
            {crops.length === 0 ? (
              <p className="no-data">No products available for purchase at the moment.</p>
            ) : (
              <div className="grid">
                {crops.map((crop) => (
                  <motion.div
                    key={crop.id}
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setSelectedCrop(crop)}
                  >
                    <CropCard crop={crop} />
                    <button className="btn-select">Select to Buy</button>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="purchase-section">
            <button 
              onClick={() => setSelectedCrop(null)} 
              className="btn-back-secondary"
            >
              ← Choose Different Product
            </button>

            <div className="selected-crop-details">
              <h2>Selected Product</h2>
              <CropCard crop={selectedCrop} />

              <form onSubmit={handlePurchase} className="purchase-form">
                <div className="form-group">
                  <label>
                    Purchase Quantity ({selectedCrop.unit})
                    <span className="available-qty">
                      Available: {selectedCrop.quantity} {selectedCrop.unit}
                    </span>
                  </label>
                  <input
                    type="number"
                    value={purchaseQuantity}
                    onChange={(e) => setPurchaseQuantity(e.target.value)}
                    required
                    min="0.01"
                    max={selectedCrop.quantity}
                    step="0.01"
                    placeholder={`Enter quantity (max: ${selectedCrop.quantity})`}
                  />
                </div>

                <div className="price-summary">
                  <p>Price per {selectedCrop.unit}: ₹{selectedCrop.price_per_unit}</p>
                  {purchaseQuantity && (
                    <p className="total-price">
                      Total: ₹{(purchaseQuantity * selectedCrop.price_per_unit).toFixed(2)}
                    </p>
                  )}
                </div>

                <motion.button
                  type="submit"
                  className="btn-submit"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  disabled={loading || !purchaseQuantity}
                >
                  {loading ? 'Processing...' : '✓ Confirm Purchase'}
                </motion.button>
              </form>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default BuyFromRetailer;
