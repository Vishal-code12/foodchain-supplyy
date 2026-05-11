import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Satheesh@11')
    MYSQL_DB = os.getenv('MYSQL_DB', 'foodchain_supply')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Blockchain
    BLOCKCHAIN_FILE = os.path.join(os.path.dirname(__file__), 'static/blockchain/blockchain_data.json')

    # Markup percentages applied at each hop (as decimal fractions)
    # Example: 0.20 means 20% markup when retailer purchases from farmer
    RETAILER_MARKUP = float(os.getenv('RETAILER_MARKUP', 0.20))
    DISTRIBUTOR_MARKUP = float(os.getenv('DISTRIBUTOR_MARKUP', 0.15))

    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)