from flask import Blueprint, jsonify, send_file
from database import get_db_connection
from middleware.auth_middleware import token_required
import qrcode
from io import BytesIO
import os
from config import Config

qr_bp = Blueprint('qr', __name__, url_prefix='/api/qr')

@qr_bp.route('/crop/<int:crop_id>', methods=['GET'])
@token_required
def generate_crop_qr(current_user, crop_id):
    """Generate QR code for a specific crop/product"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM crops WHERE id = %s", (crop_id,))
        crop = cursor.fetchone()
        
        if not crop:
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop not found"}), 404
        
        cursor.close()
        conn.close()
        
        # Create QR code data - URL to trace the product using trace_id
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        if crop.get('trace_id'):
            qr_data = f"{frontend_url}/trace?trace_id={crop['trace_id']}"
        else:
            # Fallback to crop_id if trace_id not available
            qr_data = f"{frontend_url}/trace?crop_id={crop_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return jsonify({"error": "Failed to generate QR code"}), 500

@qr_bp.route('/crop/<int:crop_id>/data', methods=['GET'])
@token_required
def get_qr_data(current_user, crop_id):
    """Get QR code data URL for a crop (returns JSON with QR code as base64)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM crops WHERE id = %s", (crop_id,))
        crop = cursor.fetchone()
        
        if not crop:
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop not found"}), 404
        
        cursor.close()
        conn.close()
        
        # Create QR code data
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        qr_data = f"{frontend_url}/trace?crop_id={crop_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        import base64
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return jsonify({
            "crop_id": crop_id,
            "trace_id": crop.get('trace_id'),
            "crop_name": crop['name'],
            "qr_data_url": qr_data,
            "qr_image_base64": f"data:image/png;base64,{img_base64}"
        }), 200
        
    except Exception as e:
        print(f"Error generating QR code data: {str(e)}")
        return jsonify({"error": "Failed to generate QR code"}), 500

