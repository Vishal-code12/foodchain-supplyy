import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import './cropCard.css';

import { useState, useEffect } from 'react';

const CropCard = ({ crop, onBuy, showBuyButton = false, userRole }) => {
  const navigate = useNavigate();
  const [quantityToBuy, setQuantityToBuy] = useState(1);

  useEffect(() => {
    const available = parseFloat(crop?.quantity) || 1;
    // Default to 1 or the available quantity if it's less than 1
    setQuantityToBuy(available >= 1 ? 1 : available);
  }, [crop]);
  const handleBuyClick = () => {
    if (onBuy) {
      const qty = parseFloat(quantityToBuy) || 1;
      onBuy(crop.id, qty);
    }
  };

  const handleTraceClick = () => {
    if (crop.trace_id) {
      navigate(`/trace?trace_id=${crop.trace_id}`);
    }
  };

  const handleCopyTraceId = (e) => {
    e.stopPropagation();
    if (crop.trace_id) {
      navigator.clipboard.writeText(crop.trace_id);
      alert(`Trace ID ${crop.trace_id} copied to clipboard!`);
    }
  };

  return (
    <motion.div 
      className="crop-card"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ 
        y: -8, 
        boxShadow: "0 12px 30px rgba(44, 85, 48, 0.3)",
        transition: { duration: 0.3 }
      }}
    >
      {crop.image_path && (
        <motion.img 
          src={`http://localhost:5000/static/uploads/${crop.image_path}`} 
          alt={crop.name}
          className="crop-image"
          whileHover={{ scale: 1.05 }}
          transition={{ duration: 0.3 }}
        />
      )}
      
      <div className="crop-info">
        <h3 className="crop-name">{crop.name}</h3>
        <p className="crop-description">{crop.description}</p>
        
        <div className="crop-details">
          {crop.trace_id && (
            <div className="detail trace-id">
              <span className="label">Trace ID:</span>
              <span className="value trace-id-value">
                {crop.trace_id}
                <button 
                  className="copy-btn" 
                  onClick={handleCopyTraceId}
                  title="Copy Trace ID"
                >
                  📋
                </button>
                <button 
                  className="trace-btn" 
                  onClick={handleTraceClick}
                  title="Trace this product"
                >
                  🔍 Trace
                </button>
              </span>
            </div>
          )}
          
          <div className="detail">
            <span className="label">Quantity:</span>
            <span className="value">{crop.quantity} {crop.unit}</span>
          </div>
          
          <div className="detail">
            <span className="label">Price:</span>
            <span className="value">₹{crop.price_per_unit} per {crop.unit}</span>
          </div>
          
          <div className="detail">
            <span className="label">Category:</span>
            <span className="value">{crop.category}</span>
          </div>
          
          {crop.location && (
            <div className="detail">
              <span className="label">Location:</span>
              <span className="value">{crop.location}</span>
            </div>
          )}
          
          {crop.farmer_name && (
            <div className="detail">
              <span className="label">Farmer:</span>
              <span className="value">{crop.farmer_name}</span>
            </div>
          )}
          
          {crop.retailer_name && (
            <div className="detail">
              <span className="label">Retailer:</span>
              <span className="value">{crop.retailer_name}</span>
            </div>
          )}
          
          {crop.distributor_name && (
            <div className="detail">
              <span className="label">Distributor:</span>
              <span className="value">{crop.distributor_name}</span>
            </div>
          )}
        </div>
        
        {showBuyButton && onBuy && (
          <div className="buy-controls">
            <label className="quantity-label">Qty:</label>
            <input
              type="number"
              className="quantity-input"
              min="0.01"
              step="0.01"
              max={crop.quantity}
              value={quantityToBuy}
              onChange={(e) => setQuantityToBuy(e.target.value)}
            />
            <button 
              className="buy-button"
              onClick={handleBuyClick}
            >
              Buy {userRole === 'customer' ? 'Product' : 'Crop'}
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default CropCard;