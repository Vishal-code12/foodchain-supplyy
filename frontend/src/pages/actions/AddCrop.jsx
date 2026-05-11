import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { farmerAPI } from '../../api/farmerAPI';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import './actions.css';

const AddCrop = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    quantity: '',
    unit: 'kg',
    price_per_unit: '',
    total_price: '',
    category: 'vegetables',
    harvest_date: '',
    expiry_date: '',
    location: ''
  });
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState('');

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleImageChange = (e) => {
    setImage(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = new FormData();
      Object.keys(formData).forEach(key => {
        data.append(key, formData[key]);
      });
      
      if (image) {
        data.append('image', image);
      }

      await farmerAPI.addCrop(data);
      setMessage('Crop added successfully!');
      setTimeout(() => {
        navigate('/farmer-dashboard');
      }, 1500);
    } catch (error) {
      console.error('Error adding crop:', error);
      setMessage(error.response?.data?.error || 'Failed to add crop');
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
          <h1>🌾 Add New Crop</h1>
          <button onClick={() => navigate('/farmer-dashboard')} className="btn-back">
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

        <form onSubmit={handleSubmit} className="action-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Crop Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                placeholder="e.g., Organic Tomatoes"
              />
            </div>

            <div className="form-group">
              <label>Category *</label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
              >
                <option value="vegetables">Vegetables</option>
                <option value="fruits">Fruits</option>
                <option value="grains">Grains</option>
                <option value="dairy">Dairy</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label>Quantity *</label>
              <input
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
                placeholder="100"
              />
            </div>

            <div className="form-group">
              <label>Unit *</label>
              <select
                name="unit"
                value={formData.unit}
                onChange={handleInputChange}
                required
              >
                <option value="kg">Kilograms (kg)</option>
                <option value="g">Grams (g)</option>
                <option value="l">Liters (l)</option>
                <option value="pieces">Pieces</option>
              </select>
            </div>

            <div className="form-group">
              <label>Price per Unit *</label>
              <input
                type="number"
                name="price_per_unit"
                value={formData.price_per_unit}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
                placeholder="50"
              />
            </div>

            <div className="form-group">
              <label>Total Price *</label>
              <input
                type="number"
                name="total_price"
                value={formData.total_price}
                onChange={handleInputChange}
                required
                min="0"
                step="0.01"
                placeholder="5000"
              />
            </div>

            <div className="form-group">
              <label>Harvest Date *</label>
              <input
                type="date"
                name="harvest_date"
                value={formData.harvest_date}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Expiry Date *</label>
              <input
                type="date"
                name="expiry_date"
                value={formData.expiry_date}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group full-width">
              <label>Location *</label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                required
                placeholder="Farm location, City, State"
              />
            </div>

            <div className="form-group full-width">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows="4"
                placeholder="Describe your crop quality, farming methods, etc."
              />
            </div>

            <div className="form-group full-width">
              <label>Crop Image</label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="file-input"
              />
            </div>
          </div>

          <motion.button
            type="submit"
            className="btn-submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            disabled={loading}
          >
            {loading ? 'Adding Crop...' : '✓ Add Crop'}
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
};

export default AddCrop;
