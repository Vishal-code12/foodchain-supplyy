import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import './Home.css';

const Home = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-page">
      <motion.header 
        className="hero-section"
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <motion.h1
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          🌱 FoodChain Supply
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          Transparent, Blockchain-powered Food Supply Chain
        </motion.p>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          From Farm to Table - Track Every Step
        </motion.p>
        
        {isAuthenticated && user ? (
          <motion.div 
            className="auth-buttons"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          >
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link to={`/${user.role}-dashboard`} className="btn primary">
                📊 Go to Dashboard
              </Link>
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.08, rotate: [0, -2, 2, -2, 0] }}
              whileTap={{ scale: 0.95 }}
              animate={{ 
                y: [0, -5, 0],
                boxShadow: [
                  "0 4px 15px rgba(46, 204, 113, 0.3)",
                  "0 8px 25px rgba(46, 204, 113, 0.5)",
                  "0 4px 15px rgba(46, 204, 113, 0.3)"
                ]
              }}
              transition={{ 
                y: { repeat: Infinity, duration: 2, ease: "easeInOut" },
                boxShadow: { repeat: Infinity, duration: 2, ease: "easeInOut" }
              }}
            >
              <Link to="/trace" className="btn trace-btn">
                🔍 Trace a Product
              </Link>
            </motion.div>
          </motion.div>
        ) : (
          <motion.div 
            className="auth-buttons"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8, duration: 0.6 }}
          >
            <Link to="/login" className="btn primary">
              📧 Login with Email
            </Link>
            <Link to="/metamask-login" className="btn primary">
              🦊 Login with MetaMask
            </Link>
            <Link to="/register" className="btn secondary">
              📝 Register
            </Link>
          </motion.div>
        )}
      </motion.header>

      <motion.section 
        className="features-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <motion.h2
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          How It Works
        </motion.h2>
        <div className="features-grid">
          <motion.div 
            className="feature"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <h3>👨‍🌾 Farmers</h3>
            <p>Add crops to the blockchain with images and details</p>
          </motion.div>
          <motion.div 
            className="feature"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <h3>🛒 Retailers</h3>
            <p>Purchase from farmers with transparent pricing</p>
          </motion.div>
          <motion.div 
            className="feature"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.5 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <h3>🚚 Distributors</h3>
            <p>Distribute products to retailers efficiently</p>
          </motion.div>
          <motion.div 
            className="feature"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.5 }}
            whileHover={{ scale: 1.05, boxShadow: "0 10px 30px rgba(0,0,0,0.2)" }}
          >
            <h3>🏪 Customers</h3>
            <p>Buy with confidence knowing the product journey</p>
          </motion.div>
        </div>
      </motion.section>

      <motion.section 
        className="how-it-works-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <motion.h2
          initial={{ opacity: 0, y: -20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          How It Works
        </motion.h2>
        <div className="steps-container">
          <motion.div 
            className="step"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="step-number">1</div>
            <h3>🌾 Farmer Registers Crop</h3>
            <p>Farmers add their products with details like origin, quality, and quantity</p>
          </motion.div>

          <motion.div 
            className="step"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="step-number">2</div>
            <h3>🏪 Retailer Purchases</h3>
            <p>Retailers buy products and transaction is recorded on blockchain</p>
          </motion.div>

          <motion.div 
            className="step"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="step-number">3</div>
            <h3>🚚 Distributor Delivers</h3>
            <p>Distributors transport products with real-time tracking</p>
          </motion.div>

          <motion.div 
            className="step"
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.5 }}
            whileHover={{ scale: 1.05 }}
          >
            <div className="step-number">4</div>
            <h3>👨‍👩‍👧‍👦 Customer Traces</h3>
            <p>Scan QR code to see complete journey from farm to table</p>
          </motion.div>
        </div>
      </motion.section>

      <motion.section 
        className="stats-section"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <div className="stats-grid">
          <motion.div 
            className="stat-card"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1, duration: 0.5 }}
            whileHover={{ scale: 1.08, y: -5 }}
          >
            <div className="stat-icon">🌾</div>
            <h3>100%</h3>
            <p>Transparent Supply Chain</p>
          </motion.div>

          <motion.div 
            className="stat-card"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2, duration: 0.5 }}
            whileHover={{ scale: 1.08, y: -5 }}
          >
            <div className="stat-icon">🔒</div>
            <h3>Secure</h3>
            <p>Blockchain Protected</p>
          </motion.div>

          <motion.div 
            className="stat-card"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3, duration: 0.5 }}
            whileHover={{ scale: 1.08, y: -5 }}
          >
            <div className="stat-icon">⚡</div>
            <h3>Real-Time</h3>
            <p>Instant Tracking Updates</p>
          </motion.div>

          <motion.div 
            className="stat-card"
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.4, duration: 0.5 }}
            whileHover={{ scale: 1.08, y: -5 }}
          >
            <div className="stat-icon">✅</div>
            <h3>Verified</h3>
            <p>Quality Assured Products</p>
          </motion.div>
        </div>
      </motion.section>

      <motion.section 
        className="blockchain-section"
        initial={{ opacity: 0, scale: 0.9 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8 }}
      >
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          🔗 Powered by Blockchain Technology
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          Every transaction is recorded on our immutable blockchain, ensuring complete transparency and trust in your food supply chain. 
          With MetaMask integration, you can authenticate using your Web3 wallet for enhanced security.
        </motion.p>
      </motion.section>
    </div>
  );
};

export default Home;