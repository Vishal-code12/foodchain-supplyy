from flask import Blueprint, request, jsonify
from database import get_db_connection
from middleware.auth_middleware import token_required
from blockchain import Blockchain
from config import Config
from utils.trace_id_generator import generate_trace_id

retailer_bp = Blueprint('retailer', __name__, url_prefix='/api/retailer')
bc = Blockchain()

@retailer_bp.route('/available-crops', methods=['GET'])
@token_required
def get_available_crops(current_user):
    """Get all available crops from farmers with search and filtering"""
    try:
        # Get query parameters for filtering
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        location = request.args.get('location', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, price, name, quantity
        sort_order = request.args.get('sort_order', 'desc').lower()  # asc or desc
        
        # Validate sort parameters
        valid_sort_fields = ['created_at', 'price_per_unit', 'name', 'quantity']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        # Map sort_by to actual column names
        sort_mapping = {
            'price_per_unit': 'c.price_per_unit',
            'name': 'c.name',
            'quantity': 'c.quantity',
            'created_at': 'c.created_at'
        }
        sort_column = sort_mapping.get(sort_by, 'c.created_at')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Build WHERE clause dynamically
        where_conditions = [
            "c.status = 'available'",
            "c.current_owner_id = c.farmer_id"
        ]
        params = []
        
        if search:
            where_conditions.append("(c.name LIKE %s OR c.description LIKE %s OR u.name LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if category:
            where_conditions.append("c.category = %s")
            params.append(category)
        
        if min_price is not None:
            where_conditions.append("c.price_per_unit >= %s")
            params.append(min_price)
        
        if max_price is not None:
            where_conditions.append("c.price_per_unit <= %s")
            params.append(max_price)
        
        if location:
            where_conditions.append("c.location LIKE %s")
            params.append(f"%{location}%")
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
            SELECT 
                c.id,
                c.name,
                c.description,
                c.quantity,
                c.unit,
                c.price_per_unit,
                c.image_path,
                c.category,
                c.harvest_date,
                c.expiry_date,
                c.location,
                u.name as farmer_name,
                u.phone as farmer_phone,
                c.created_at
            FROM crops c
            JOIN users u ON c.farmer_id = u.id
            WHERE {where_clause}
            ORDER BY {sort_column} {sort_order.upper()}
        """
        
        cursor.execute(query, params)

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
                "farmer_name": crop['farmer_name'],
                "farmer_phone": crop['farmer_phone'],
                "created_at": crop['created_at'].isoformat() if crop['created_at'] else None
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_crops), 200

    except Exception as e:
        print(f"Error fetching available crops: {str(e)}")
        return jsonify({"error": "Failed to fetch available crops"}), 500

@retailer_bp.route('/buy', methods=['POST'])
@token_required
def buy_crop(current_user):
    """Retailer buys crop from farmer"""
    if current_user['role'] != 'retailer':
        return jsonify({"error": "Only retailers can buy crops"}), 403

    conn = None
    cursor = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        crop_id = data.get('crop_id')
        quantity = data.get('quantity')

        if not crop_id:
            return jsonify({"error": "crop_id is required"}), 400

        # Convert to proper types
        try:
            crop_id = int(crop_id)
            if quantity is not None:
                quantity = float(quantity)
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid data types"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch crop with lock to prevent race conditions
        cursor.execute("SELECT * FROM crops WHERE id = %s FOR UPDATE", (crop_id,))
        crop = cursor.fetchone()
        
        if not crop:
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop not found"}), 404
        
        if crop['status'] != 'available':
            cursor.close()
            conn.close()
            return jsonify({"error": f"Crop not available. Current status: {crop['status']}"}), 400

        # Verify the crop is still with the farmer
        if crop['current_owner_id'] != crop['farmer_id']:
            cursor.close()
            conn.close()
            return jsonify({"error": "Crop is no longer available for purchase"}), 400

        # Set default quantity to available quantity if not provided
        available_quantity = float(crop['quantity'])
        if quantity is None:
            quantity = available_quantity
        elif quantity <= 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Quantity must be greater than 0"}), 400
        elif available_quantity < quantity:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Insufficient quantity. Available: {available_quantity}, Requested: {quantity}"}), 400

        # Calculate price with retailer markup applied to the farmer's price_per_unit
        base_price_per_unit = float(crop['price_per_unit'])
        retailer_price_per_unit = round(base_price_per_unit * (1 + Config.RETAILER_MARKUP), 4)

        # Update crop ownership and quantity, applying markup for retailer's portion
        purchased_crop_id = None
        if quantity == available_quantity:
            # Full purchase - transfer entire crop to retailer and update its price_per_unit
            cursor.execute("""
                UPDATE crops 
                SET current_owner_id = %s, status = 'sold', price_per_unit = %s
                WHERE id = %s
            """, (current_user['id'], retailer_price_per_unit, crop_id))
            purchased_crop_id = crop_id
            total_price = retailer_price_per_unit * quantity
        else:
            # Partial purchase - reduce quantity and create new crop for retailer
            remaining_quantity = available_quantity - quantity
            
            # Update original crop with reduced quantity
            cursor.execute("""
                UPDATE crops 
                SET quantity = %s 
                WHERE id = %s
            """, (remaining_quantity, crop_id))
            
            # Create new crop record for the purchased portion with a unique trace_id
            # Check if trace_id column exists before including it
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
                      quantity, crop['unit'], retailer_price_per_unit, crop['image_path'],
                      crop['category'], crop['harvest_date'], crop['expiry_date'], 
                      crop['location'], 'sold', new_trace_id))
            else:
                cursor.execute("""
                    INSERT INTO crops 
                    (farmer_id, current_owner_id, name, description, quantity, unit, 
                     price_per_unit, image_path, category, harvest_date, expiry_date, location, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (crop['farmer_id'], current_user['id'], crop['name'], crop['description'],
                      quantity, crop['unit'], retailer_price_per_unit, crop['image_path'],
                      crop['category'], crop['harvest_date'], crop['expiry_date'], 
                      crop['location'], 'sold'))
            
            purchased_crop_id = cursor.lastrowid
            total_price = retailer_price_per_unit * quantity

        # Create transaction record in blockchain table
        block_data = {
            "crop_id": crop_id,
            "purchased_crop_id": purchased_crop_id,
            "from_farmer_id": crop['farmer_id'],
            "to_retailer_id": current_user['id'],
            "quantity": quantity,
            "price_per_unit": retailer_price_per_unit,
            "total_price": total_price,
            "transaction_type": "partial" if quantity < available_quantity else "full"
        }
        
        # Add to blockchain
        block = bc.add_block("FARMER_TO_RETAILER", block_data)

        # Also store in transactions table
        # IMPORTANT: Use purchased_crop_id (the new crop created) for partial purchases
        # This ensures the transaction is linked to the actual crop the buyer receives
        cursor.execute("""
            INSERT INTO transactions 
            (crop_id, from_user_id, to_user_id, transaction_type, quantity, price, block_hash, previous_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (purchased_crop_id, crop['farmer_id'], current_user['id'], 'farmer_to_retailer', 
              quantity, total_price, block['hash'], block['previous_hash']))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Purchase successful",
            "quantity_purchased": quantity,
            "total_price": total_price,
            "purchased_crop_id": purchased_crop_id if quantity < available_quantity else crop_id,
            "blockchain_block": block['index']
        }), 201

    except Exception as e:
        print(f"Error in buy_crop: {str(e)}")
        import traceback
        traceback.print_exc()
        # Ensure database connection is closed on error
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()
        return jsonify({"error": str(e)}), 500

@retailer_bp.route('/my-purchases', methods=['GET'])
@token_required
def get_my_purchases(current_user):
    """Get all purchases made by retailer"""
    if current_user['role'] != 'retailer':
        return jsonify({"error": "Only retailers can view purchases"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                t.*,
                c.name as crop_name,
                u.name as farmer_name,
                c.image_path
            FROM transactions t
            JOIN crops c ON t.crop_id = c.id
            JOIN users u ON t.from_user_id = u.id
            WHERE t.to_user_id = %s 
            AND t.transaction_type = 'farmer_to_retailer'
            ORDER BY t.timestamp DESC
        """, (current_user['id'],))

        purchases = cursor.fetchall()
        
        formatted_purchases = []
        for purchase in purchases:
            formatted_purchases.append({
                "id": purchase['id'],
                "crop_name": purchase['crop_name'],
                "farmer_name": purchase['farmer_name'],
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

@retailer_bp.route('/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    """Get retailer's current inventory"""
    if current_user['role'] != 'retailer':
        return jsonify({"error": "Only retailers can view inventory"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM crops 
            WHERE current_owner_id = %s 
            AND status = 'sold'
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