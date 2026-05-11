import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { traceAPI } from '../../api/traceAPI';
import ChainViewer from '../../components/traceability/ChainViewer';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import './trace.css';

const ProductTrace = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [traceId, setTraceId] = useState('');
  const [journey, setJourney] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check for trace_id in URL parameters
  useEffect(() => {
    const urlTraceId = searchParams.get('trace_id');
    const urlCropId = searchParams.get('crop_id'); // Fallback for old URLs
    if (urlTraceId) {
      setTraceId(urlTraceId);
      // Auto-trace when trace_id is in URL
      setLoading(true);
      setError('');
      setJourney(null);
      traceAPI.getCropJourney(urlTraceId)
        .then(response => {
          setJourney(response.data);
        })
        .catch(err => {
          console.error('Error fetching journey:', err);
          setError(err.response?.data?.error || 'Failed to fetch product journey');
        })
        .finally(() => {
          setLoading(false);
        });
    } else if (urlCropId) {
      // For backward compatibility, try to get trace_id from crop_id
      setTraceId(urlCropId);
    }
  }, [searchParams]);

  const handleAutoTrace = async (id) => {
    setLoading(true);
    setError('');
    setJourney(null);
    try {
      const response = await traceAPI.getCropJourney(id);
      setJourney(response.data);
    } catch (err) {
      console.error('Error fetching journey:', err);
      setError(err.response?.data?.error || 'Failed to fetch product journey');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!traceId.trim()) return;

    setLoading(true);
    setError('');
    setJourney(null);

    try {
      const response = await traceAPI.getCropJourney(traceId);
      setJourney(response.data);
    } catch (err) {
      console.error('Error fetching journey:', err);
      setError(err.response?.data?.error || 'Failed to fetch product journey');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trace-container">
      <div className="trace-header">
        <h1>🔍 Product Traceability</h1>
        <p>Track the complete journey of any product from farm to table</p>
      </div>

      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <div className="form-group">
            <label htmlFor="traceId">Enter Trace ID to Trace Product</label>
            <input
              type="text"
              id="traceId"
              value={traceId}
              onChange={(e) => setTraceId(e.target.value)}
              placeholder="e.g., 123456, 789012..."
              required
              pattern="[0-9]{6,}"
              title="Enter a 6-digit or longer trace ID"
            />
            <small className="form-hint">Trace ID is a 6+ digit number found on product labels</small>
          </div>
          <button type="submit" className="btn primary" disabled={loading}>
            {loading ? 'Searching...' : 'Trace Product'}
          </button>
        </form>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading && <LoadingSpinner message="Loading product journey..." />}

      {journey && !loading && (
        <div className="journey-section">
          <div className="crop-summary">
            <h2>Product Information</h2>
            <div className="summary-card">
              <h3>{journey.crop.name}</h3>
              <p>{journey.crop.description}</p>
              <div className="summary-details">
                {journey.crop.trace_id && (
                  <span><strong>Trace ID:</strong> {journey.crop.trace_id}</span>
                )}
                <span><strong>Current Owner:</strong> {journey.crop.current_owner}</span>
                <span><strong>Status:</strong> {journey.crop.current_status}</span>
                <span><strong>Total Steps:</strong> {journey.total_steps}</span>
              </div>
              {journey.crop.image_path && (
                <img 
                  src={`http://localhost:5000/static/uploads/${journey.crop.image_path}`}
                  alt={journey.crop.name}
                  className="crop-image-large"
                />
              )}
            </div>
          </div>

          <ChainViewer journey={journey.journey} />
        </div>
      )}

      {!journey && !loading && !error && (
        <div className="placeholder-section">
          <div className="placeholder-content">
            <h3>How to Use Product Traceability</h3>
            <ol>
              <li>Enter the Trace ID from any product you've purchased</li>
              <li>View the complete journey from farmer to your table</li>
              <li>See all transactions recorded on the blockchain</li>
              <li>Verify the authenticity and origin of your food</li>
            </ol>
            <div className="features">
              <div className="feature">
                <h4>🌱 Farm Origin</h4>
                <p>See exactly which farm your food came from</p>
              </div>
              <div className="feature">
                <h4>⛓️ Supply Chain</h4>
                <p>Track every step through the supply chain</p>
              </div>
              <div className="feature">
                <h4>🔗 Blockchain Verified</h4>
                <p>All transactions are immutable and transparent</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductTrace;