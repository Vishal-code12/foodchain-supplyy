from flask import Blueprint, request, jsonify
from database import get_db_connection
from middleware.auth_middleware import token_required
from blockchain import Blockchain
import os
import sys
from pathlib import Path
# Add backend directory to path for utils import
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
from utils.trace_id_generator import generate_trace_id
from config import Config
from werkzeug.utils import secure_filename

farmer_bp = Blueprint('farmer', __name__, url_prefix='/api/farmer')
bc = Blockchain()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@farmer_bp.route('/crops', methods=['POST'])
@token_required
def add_crop(current_user):
    if current_user['role'] != 'farmer':
        return jsonify({"error": "Only farmers can add crops"}), 403

    try:
        # Handle file upload
        image_file = request.files.get('image')
        image_path = None

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join('crops', filename)
            full_path = os.path.join(Config.UPLOAD_FOLDER, 'crops', filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            image_file.save(full_path)

        data = request.form
        name = data.get('name')
        description = data.get('description')
        quantity = data.get('quantity')
        unit = data.get('unit', 'kg')
        price_per_unit = data.get('price_per_unit')
        # Support bulk total price input: if farmer provides total_price (bulk price) and quantity,
        # compute price_per_unit = total_price / quantity
        total_price = data.get('total_price')
        if (not price_per_unit or price_per_unit == '') and total_price and quantity:
            try:
                qty_val = float(quantity)
                total_val = float(total_price)
                if qty_val <= 0:
                    return jsonify({"error": "Quantity must be greater than 0"}), 400
                price_per_unit = total_val / qty_val
            except Exception:
                return jsonify({"error": "Invalid quantity or total_price"}), 400
        category = data.get('category', 'vegetables')
        harvest_date = data.get('harvest_date')
        expiry_date = data.get('expiry_date')
        location = data.get('location')

        if not all([name, quantity, price_per_unit]):
            return jsonify({"error": "Missing required fields"}), 400

        # Generate unique trace ID
        trace_id = generate_trace_id()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if trace_id column exists
        cursor.execute("SHOW COLUMNS FROM crops LIKE 'trace_id'")
        trace_id_column_exists = cursor.fetchone()

        print(f"Adding crop - trace_id column exists: {trace_id_column_exists is not None}, generated trace_id: {trace_id}")

        if trace_id_column_exists:
            # Column exists - insert with trace_id
            try:
                cursor.execute(
                    """INSERT INTO crops 
                    (farmer_id, current_owner_id, name, description, quantity, unit, price_per_unit, 
                     image_path, category, harvest_date, expiry_date, location, trace_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (current_user['id'], current_user['id'], name, description, float(quantity), unit,
                     float(price_per_unit), image_path, category, harvest_date, expiry_date, location, trace_id)
                )
                print(f"Successfully inserted crop with trace_id: {trace_id}")
            except Exception as insert_error:
                print(f"Error inserting with trace_id: {insert_error}")
                # Fallback: try without trace_id
                cursor.execute(
                    """INSERT INTO crops 
                    (farmer_id, current_owner_id, name, description, quantity, unit, price_per_unit, 
                     image_path, category, harvest_date, expiry_date, location) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (current_user['id'], current_user['id'], name, description, float(quantity), unit,
                     float(price_per_unit), image_path, category, harvest_date, expiry_date, location)
                )
                trace_id = None
        else:
            # Column doesn't exist yet - insert without trace_id
            print("Warning: trace_id column not found. Inserting crop without trace_id.")
            cursor.execute(
                """INSERT INTO crops 
                (farmer_id, current_owner_id, name, description, quantity, unit, price_per_unit, 
                 image_path, category, harvest_date, expiry_date, location) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (current_user['id'], current_user['id'], name, description, float(quantity), unit,
                 float(price_per_unit), image_path, category, harvest_date, expiry_date, location)
            )
            trace_id = None  # Set to None if column doesn't exist
        crop_id = cursor.lastrowid

        # Add to blockchain
        block_data = {
            "crop_id": crop_id,
            "farmer_id": current_user['id'],
            "name": name,
            "quantity": float(quantity),
            "action": "crop_added"
        }
        block = bc.add_block("CROP_ADDED", block_data)

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Crop added successfully",
            "crop_id": crop_id,
            "trace_id": trace_id,
            "blockchain_block": block['index']
        }), 201

    except Exception as e:
        print(f"Error adding crop: {str(e)}")
        return jsonify({"error": "Failed to add crop"}), 500

@farmer_bp.route('/my-crops', methods=['GET'])
@token_required
def get_my_crops(current_user):
    if current_user['role'] != 'farmer':
        return jsonify({"error": "Only farmers can view their crops"}), 403

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if trace_id column exists
        cursor.execute("SHOW COLUMNS FROM crops LIKE 'trace_id'")
        trace_id_column_exists = cursor.fetchone()
        
        # Build SELECT query - explicitly include trace_id if column exists
        if trace_id_column_exists:
            cursor.execute("""
                SELECT id, farmer_id, current_owner_id, name, description, quantity, unit, 
                       price_per_unit, image_path, category, status, harvest_date, expiry_date, 
                       location, trace_id, created_at, updated_at
                FROM crops 
                WHERE farmer_id = %s 
                ORDER BY created_at DESC
            """, (current_user['id'],))
        else:
            cursor.execute("""
                SELECT id, farmer_id, current_owner_id, name, description, quantity, unit, 
                       price_per_unit, image_path, category, status, harvest_date, expiry_date, 
                       location, created_at, updated_at
                FROM crops 
                WHERE farmer_id = %s 
                ORDER BY created_at DESC
            """, (current_user['id'],))

        crops = cursor.fetchall()
        
        # Format response
        formatted_crops = []
        for crop in crops:
            formatted_crops.append({
                "id": crop['id'],
                "trace_id": crop.get('trace_id') if trace_id_column_exists else None,
                "name": crop['name'],
                "description": crop['description'],
                "quantity": float(crop['quantity']),
                "unit": crop['unit'],
                "price_per_unit": float(crop['price_per_unit']),
                "image_path": crop['image_path'],
                "category": crop['category'],
                "status": crop['status'],
                "harvest_date": crop['harvest_date'].isoformat() if crop['harvest_date'] else None,
                "expiry_date": crop['expiry_date'].isoformat() if crop['expiry_date'] else None,
                "location": crop['location'],
                "created_at": crop['created_at'].isoformat() if crop['created_at'] else None
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_crops), 200

    except Exception as e:
        print(f"Error fetching crops: {str(e)}")
        return jsonify({"error": "Failed to fetch crops"}), 500

@farmer_bp.route('/available-crops', methods=['GET'])
@token_required
def get_available_crops(current_user):
    """Get all available crops from all farmers (for other roles to see) with search and filtering"""
    try:
        # Get query parameters for filtering
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        location = request.args.get('location', '').strip()
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc').lower()
        
        valid_sort_fields = ['created_at', 'price_per_unit', 'name', 'quantity']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'
        
        sort_mapping = {
            'price_per_unit': 'c.price_per_unit',
            'name': 'c.name',
            'quantity': 'c.quantity',
            'created_at': 'c.created_at'
        }
        sort_column = sort_mapping.get(sort_by, 'c.created_at')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        where_conditions = ["c.status = 'available'"]
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
                c.*,
                u.name as farmer_name,
                u.email as farmer_email,
                u.phone as farmer_phone
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
                "farmer_email": crop['farmer_email'],
                "farmer_phone": crop['farmer_phone'],
                "created_at": crop['created_at'].isoformat() if crop['created_at'] else None
            })

        cursor.close()
        conn.close()

        return jsonify(formatted_crops), 200

    except Exception as e:
        print(f"Error fetching available crops: {str(e)}")
        return jsonify({"error": "Failed to fetch available crops"}), 500