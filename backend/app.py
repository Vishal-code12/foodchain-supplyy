from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db

# Import routes
from routes.auth_routes import auth_bp
from routes.farmer_routes import farmer_bp
from routes.retailer_routes import retailer_bp
from routes.distributor_routes import distributor_bp
from routes.customer_routes import customer_bp
from routes.trace_routes import trace_bp
from routes.qr_routes import qr_bp
from routes.analytics_routes import analytics_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app)

    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(farmer_bp)
    app.register_blueprint(retailer_bp)
    app.register_blueprint(distributor_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(trace_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(analytics_bp)

    # Health check route
    @app.route('/')
    def health_check():
        return {"status": "OK", "message": "FoodChain Supply Backend is running!"}

    return app

if __name__ == '__main__':
    import os
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)