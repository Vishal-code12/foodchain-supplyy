import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMetaMask } from '../../context/MetaMaskContext';
import { useAuth } from '../../context/AuthContext';
import '../../pages/auth/auth.css';

const MetaMaskLogin = () => {
  const navigate = useNavigate();
  const { account, connectWallet, signMessage, isConnecting, error: walletError, isMetaMaskInstalled } = useMetaMask();
  const { loginWithMetaMask } = useAuth();
  const [selectedRole, setSelectedRole] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleMetaMaskLogin = async () => {
    setError('');
    
    if (!selectedRole) {
      setError('Please select your role');
      return;
    }

    setLoading(true);

    try {
      // Step 1: Connect wallet if not connected
      let walletAddress = account;
      if (!walletAddress) {
        walletAddress = await connectWallet();
        if (!walletAddress) {
          setError('Failed to connect wallet');
          setLoading(false);
          return;
        }
      }

      // Step 2: Sign message for authentication
      const message = `Sign this message to login to FoodChain Supply as ${selectedRole}\nWallet: ${walletAddress}\nTimestamp: ${Date.now()}`;
      const signature = await signMessage(message);

      // Step 3: Send to backend for verification
      const result = await loginWithMetaMask(walletAddress, signature, selectedRole);
      
      if (result.success) {
        // Navigate based on role
        switch (selectedRole) {
          case 'farmer':
            navigate('/farmer-dashboard');
            break;
          case 'retailer':
            navigate('/retailer-dashboard');
            break;
          case 'distributor':
            navigate('/distributor-dashboard');
            break;
          case 'customer':
            navigate('/customer-dashboard');
            break;
          default:
            navigate('/');
        }
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      console.error('MetaMask login error:', err);
      setError(err.message || 'Failed to login with MetaMask');
    } finally {
      setLoading(false);
    }
  };

  if (!isMetaMaskInstalled) {
    return (
      <div className="metamask-login-container">
        <div className="metamask-card">
          <h2>🦊 MetaMask Required</h2>
          <p>Please install MetaMask extension to login with your wallet.</p>
          <a 
            href="https://metamask.io/download/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="btn primary"
          >
            Install MetaMask
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="metamask-login-container">
      <div className="metamask-card">
        <h2>🦊 Login with MetaMask</h2>
        <p className="subtitle">Connect your wallet to access the platform</p>

        {walletError && (
          <div className="error-message">{walletError}</div>
        )}

        {error && (
          <div className="error-message">{error}</div>
        )}

        {account && (
          <div className="wallet-info">
            <p>✅ Connected Wallet:</p>
            <code>{account.slice(0, 6)}...{account.slice(-4)}</code>
          </div>
        )}

        <div className="form-group">
          <label>Select Your Role</label>
          <select 
            value={selectedRole} 
            onChange={(e) => setSelectedRole(e.target.value)}
            className="role-select"
          >
            <option value="">-- Choose Role --</option>
            <option value="farmer">🌾 Farmer</option>
            <option value="retailer">🏪 Retailer</option>
            <option value="distributor">🚚 Distributor</option>
            <option value="customer">👤 Customer</option>
          </select>
        </div>

        <button
          onClick={handleMetaMaskLogin}
          disabled={loading || isConnecting || !selectedRole}
          className="btn primary metamask-btn"
        >
          {loading || isConnecting ? (
            '⏳ Connecting...'
          ) : account ? (
            '🔐 Sign & Login'
          ) : (
            '🦊 Connect MetaMask'
          )}
        </button>

        <div className="divider">
          <span>OR</span>
        </div>

        <button
          onClick={() => navigate('/login')}
          className="btn secondary"
        >
          Login with Email
        </button>
      </div>
    </div>
  );
};

export default MetaMaskLogin;