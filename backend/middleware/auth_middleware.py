from flask import request, jsonify
from auth import verify_token
from database import get_db_connection

def token_required(f):
    def decorated(*args, **kwargs):
        # Allow OPTIONS requests to pass through (CORS preflight)
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Safely extract token from "Bearer <token>" format
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
            elif len(parts) == 1:
                # Handle case where token is sent without "Bearer" prefix
                token = parts[0]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Get user from database with proper error handling
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (payload['sub'],))
            current_user = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Database error in auth_middleware: {str(e)}")
            return jsonify({"error": "Database error"}), 500

        if not current_user:
            return jsonify({"error": "User not found"}), 401

        return f(current_user, *args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated