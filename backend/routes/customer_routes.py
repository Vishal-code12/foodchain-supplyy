from flask import Blueprint, request, jsonify
from database import get_db_connection
from middleware.auth_middleware import token_required
from blockchain import Blockchain

customer_bp = Blueprint('customer', __name__, url_prefix='/api/customer')
bc = Blockchain()

@customer_bp.route('/available-crops', methods=['GET'])
@token_required
def get_available_crops(current_user):
    """Get crops available from distributors"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                c.*,
                u.name as distributor_name
            FROM crops c
            JOIN users u ON c.current_owner_id = u.id
            WHERE c.status = 'shipped'
            AND u.role = 'distributor'
            ORDER BY c.created_at DESC
        """)

        crops = cursor.fetchall()
        
        formatted_crops = []
        for crop in crops:
            formatted_crops.append({
                "id": crop['id'],
                "trace_id": crop.get('trace_id'),
                "name": crop['name'],
                "description": crop['description'],
                "quantity": float(crop['quantity']),
                "unit": crop['unit'],
                "price_per_unit": float(crop['price_per_unit']),
                "image_path": crop['image_path'],
                "category": crop['category'],
                "harvest_date": crop['harvest_date'].isoformat() if crop['harvest_date'] else None,
                "expiry_date": crop['expiry_date'].isoformat() if crop['expiry_date'] else None,
                "location": crop['location'],
                "distributor_name": crop['distributor_name'],
                "created_at": crop['created_at'].isoformat() if crop['created_at'] else None
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_crops), 200

    except Exception as e:
        print(f"Error fetching available crops: {str(e)}")
        return jsonify({"error": "Failed to fetch available crops"}), 500

@customer_bp.route('/buy', methods=['POST'])
@token_required
def buy_crop(current_user):
    """Customer buys crop from distributor"""
    if current_user['role'] != 'customer':
        return jsonify({"error": "Only customers can buy from distributors"}), 403

    try:
        data = request.get_json()
        crop_id = data.get('crop_id')
        quantity = data.get('quantity')

        if not crop_id:
            return jsonify({"error": "crop_id is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch crop
        cursor.execute("SELECT * FROM crops WHERE id = %s FOR UPDATE", (crop_id,))
        crop = cursor.fetchone()
        
        if not crop:
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop not found"}), 404
        
        # Verify current owner is a distributor
        cursor.execute("SELECT role FROM users WHERE id = %s", (crop['current_owner_id'],))
        owner = cursor.fetchone()
        
        if not owner or owner['role'] != 'distributor':
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop is not available from distributor"}), 400

        available_quantity = float(crop['quantity'])
        if quantity is None:
            quantity = available_quantity
        elif quantity <= 0 or quantity > available_quantity:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid quantity"}), 400

        price_per_unit = float(crop['price_per_unit'])
        total_price = price_per_unit * quantity

        # Update crop status to delivered
        cursor.execute("""
            UPDATE crops 
            SET current_owner_id = %s, status = 'delivered' 
            WHERE id = %s
        """, (current_user['id'], crop_id))

        # Add to blockchain
        block_data = {
            "crop_id": crop_id,
            "from_distributor_id": crop['current_owner_id'],
            "to_customer_id": current_user['id'],
            "quantity": quantity,
            "total_price": total_price
        }
        block = bc.add_block("DISTRIBUTOR_TO_CUSTOMER", block_data)

        # Store transaction
        cursor.execute("""
            INSERT INTO transactions 
            (crop_id, from_user_id, to_user_id, transaction_type, quantity, price, block_hash, previous_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (crop_id, crop['current_owner_id'], current_user['id'], 'distributor_to_customer', 
              quantity, total_price, block['hash'], block['previous_hash']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Purchase successful",
            "quantity": quantity,
            "total_price": total_price,
            "blockchain_block": block['index']
        }), 201

    except Exception as e:
        print(f"Error in customer buy: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@customer_bp.route('/my-purchases', methods=['GET'])
@token_required
def get_my_purchases(current_user):
    """Get all purchases made by customer from distributors"""
    if current_user['role'] != 'customer':
        return jsonify({"error": "Only customers can view purchases"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                t.*,
                c.name as crop_name,
                u.name as distributor_name,
                c.image_path
            FROM transactions t
            JOIN crops c ON t.crop_id = c.id
            JOIN users u ON t.from_user_id = u.id
            WHERE t.to_user_id = %s 
            AND t.transaction_type = 'distributor_to_customer'
            ORDER BY t.timestamp DESC
        """, (current_user['id'],))

        purchases = cursor.fetchall()
        
        formatted_purchases = []
        for purchase in purchases:
            formatted_purchases.append({
                "id": purchase['id'],
                "crop_name": purchase['crop_name'],
                "distributor_name": purchase['distributor_name'],
                "quantity": float(purchase['quantity']),
                "price": float(purchase['price']),
                "timestamp": purchase['timestamp'].isoformat() if purchase['timestamp'] else None,
                "image_path": purchase['image_path'],
                "block_hash": purchase['block_hash']
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_purchases), 200

    except Exception as e:
        print(f"Error fetching purchases: {str(e)}")
        return jsonify({"error": "Failed to fetch purchases"}), 500