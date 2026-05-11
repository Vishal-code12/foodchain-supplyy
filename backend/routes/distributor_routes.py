from flask import Blueprint, request, jsonify
from database import get_db_connection
from middleware.auth_middleware import token_required
from blockchain import Blockchain
from config import Config
from utils.trace_id_generator import generate_trace_id

distributor_bp = Blueprint('distributor', __name__, url_prefix='/api/distributor')
bc = Blockchain()

@distributor_bp.route('/available-crops', methods=['GET'])
@token_required
def get_available_crops(current_user):
    """Get crops available from retailers"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                c.*,
                u.name as retailer_name,
                u.phone as retailer_phone
            FROM crops c
            JOIN users u ON c.current_owner_id = u.id
            WHERE c.status = 'sold'
            AND u.role = 'retailer'
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
                "retailer_name": crop['retailer_name'],
                "retailer_phone": crop['retailer_phone'],
                "created_at": crop['created_at'].isoformat() if crop['created_at'] else None
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_crops), 200

    except Exception as e:
        print(f"Error fetching available crops: {str(e)}")
        return jsonify({"error": "Failed to fetch available crops"}), 500

@distributor_bp.route('/buy', methods=['POST'])
@token_required
def buy_crop(current_user):
    """Distributor buys crop from retailer"""
    if current_user['role'] != 'distributor':
        return jsonify({"error": "Only distributors can buy from retailers"}), 403

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
        
        # Verify current owner is a retailer
        cursor.execute("SELECT role FROM users WHERE id = %s", (crop['current_owner_id'],))
        owner = cursor.fetchone()
        
        if not owner or owner['role'] != 'retailer':
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop is not available from retailer"}), 400

        available_quantity = float(crop['quantity'])
        if quantity is None:
            quantity = available_quantity
        elif quantity <= 0 or quantity > available_quantity:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid quantity"}), 400

        base_price_per_unit = float(crop['price_per_unit'])
        distributor_price_per_unit = round(base_price_per_unit * (1 + Config.DISTRIBUTOR_MARKUP), 4)

        purchased_crop_id = None
        if quantity == available_quantity:
            # Full purchase - transfer entire crop to distributor and update price
            cursor.execute("""
                UPDATE crops 
                SET current_owner_id = %s, status = 'shipped', price_per_unit = %s
                WHERE id = %s
            """, (current_user['id'], distributor_price_per_unit, crop_id))
            purchased_crop_id = crop_id
            total_price = distributor_price_per_unit * quantity
        else:
            # Partial purchase - reduce quantity and create new crop for distributor
            remaining_quantity = available_quantity - quantity

            # Update original crop with reduced quantity
            cursor.execute("""
                UPDATE crops 
                SET quantity = %s 
                WHERE id = %s
            """, (remaining_quantity, crop_id))

            # Create new crop record for the purchased portion (inherit trace_id from parent)
            # Check for trace_id column existence
            cursor.execute("SHOW COLUMNS FROM crops LIKE 'trace_id'")
            trace_col = cursor.fetchone()
            if trace_col:
                new_trace_id = generate_trace_id()
                cursor.execute("""
                    INSERT INTO crops 
                    (farmer_id, current_owner_id, name, description, quantity, unit, 
                     price_per_unit, image_path, category, harvest_date, expiry_date, location, status, trace_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (crop['farmer_id'], current_user['id'], crop['name'], crop['description'],
                      quantity, crop['unit'], distributor_price_per_unit, crop['image_path'],
                      crop['category'], crop['harvest_date'], crop['expiry_date'], 
                      crop['location'], 'shipped', new_trace_id))
            else:
                cursor.execute("""
                    INSERT INTO crops 
                    (farmer_id, current_owner_id, name, description, quantity, unit, 
                     price_per_unit, image_path, category, harvest_date, expiry_date, location, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (crop['farmer_id'], current_user['id'], crop['name'], crop['description'],
                      quantity, crop['unit'], distributor_price_per_unit, crop['image_path'],
                      crop['category'], crop['harvest_date'], crop['expiry_date'], 
                      crop['location'], 'shipped'))
            purchased_crop_id = cursor.lastrowid
            total_price = distributor_price_per_unit * quantity

        # Add to blockchain
        block_data = {
            "crop_id": crop_id,
            "purchased_crop_id": purchased_crop_id,
            "from_retailer_id": crop['current_owner_id'],
            "to_distributor_id": current_user['id'],
            "quantity": quantity,
            "price_per_unit": distributor_price_per_unit,
            "total_price": total_price
        }
        block = bc.add_block("RETAILER_TO_DISTRIBUTOR", block_data)

        # Store transaction
        # IMPORTANT: Use purchased_crop_id (the new crop created) for partial purchases
        cursor.execute("""
            INSERT INTO transactions 
            (crop_id, from_user_id, to_user_id, transaction_type, quantity, price, block_hash, previous_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (purchased_crop_id, crop['current_owner_id'], current_user['id'], 'retailer_to_distributor', 
              quantity, total_price, block['hash'], block['previous_hash']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Purchase from retailer successful",
            "quantity": quantity,
            "total_price": total_price,
            "blockchain_block": block['index']
        }), 201

    except Exception as e:
        print(f"Error in distributor buy: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@distributor_bp.route('/my-purchases', methods=['GET'])
@token_required
def get_my_purchases(current_user):
    """Get all purchases made by distributor from retailers"""
    if current_user['role'] != 'distributor':
        return jsonify({"error": "Only distributors can view purchases"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                t.*,
                c.name as crop_name,
                u.name as retailer_name,
                c.image_path
            FROM transactions t
            JOIN crops c ON t.crop_id = c.id
            JOIN users u ON t.from_user_id = u.id
            WHERE t.to_user_id = %s 
            AND t.transaction_type = 'retailer_to_distributor'
            ORDER BY t.timestamp DESC
        """, (current_user['id'],))

        purchases = cursor.fetchall()
        
        formatted_purchases = []
        for purchase in purchases:
            formatted_purchases.append({
                "id": purchase['id'],
                "crop_name": purchase['crop_name'],
                "retailer_name": purchase['retailer_name'],
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

@distributor_bp.route('/my-sales', methods=['GET'])
@token_required
def get_my_sales(current_user):
    """Get all sales made by distributor to customers"""
    if current_user['role'] != 'distributor':
        return jsonify({"error": "Only distributors can view sales"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                t.*,
                c.name as crop_name,
                u.name as customer_name,
                c.image_path
            FROM transactions t
            JOIN crops c ON t.crop_id = c.id
            JOIN users u ON t.to_user_id = u.id
            WHERE t.from_user_id = %s 
            AND t.transaction_type = 'distributor_to_customer'
            ORDER BY t.timestamp DESC
        """, (current_user['id'],))

        sales = cursor.fetchall()
        
        formatted_sales = []
        for sale in sales:
            formatted_sales.append({
                "id": sale['id'],
                "crop_name": sale['crop_name'],
                "customer_name": sale['customer_name'],
                "quantity": float(sale['quantity']),
                "price": float(sale['price']),
                "timestamp": sale['timestamp'].isoformat() if sale['timestamp'] else None,
                "image_path": sale['image_path'],
                "block_hash": sale['block_hash']
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_sales), 200

    except Exception as e:
        print(f"Error fetching sales: {str(e)}")
        return jsonify({"error": "Failed to fetch sales"}), 500

@distributor_bp.route('/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    """Get distributor's current inventory"""
    if current_user['role'] != 'distributor':
        return jsonify({"error": "Only distributors can view inventory"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM crops 
            WHERE current_owner_id = %s 
            AND status = 'shipped'
            ORDER BY created_at DESC
        """, (current_user['id'],))

        inventory = cursor.fetchall()
        
        formatted_inventory = []
        for item in inventory:
            formatted_inventory.append({
                "id": item['id'],
                "trace_id": item.get('trace_id'),
                "name": item['name'],
                "description": item['description'],
                "quantity": float(item['quantity']),
                "unit": item['unit'],
                "price_per_unit": float(item['price_per_unit']),
                "image_path": item['image_path'],
                "category": item['category'],
                "harvest_date": item['harvest_date'].isoformat() if item['harvest_date'] else None,
                "expiry_date": item['expiry_date'].isoformat() if item['expiry_date'] else None,
                "location": item['location'],
                "created_at": item['created_at'].isoformat() if item['created_at'] else None
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_inventory), 200

    except Exception as e:
        print(f"Error fetching inventory: {str(e)}")
        return jsonify({"error": "Failed to fetch inventory"}), 500