from flask import Blueprint, jsonify, request
from database import get_db_connection

trace_bp = Blueprint('trace', __name__, url_prefix='/api/trace')

@trace_bp.route('/<trace_id>', methods=['GET'])
def get_crop_journey(trace_id):
    """Get complete journey of a crop from farmer to customer using trace_id or crop_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Try to find crop by trace_id first, then fallback to crop_id (for backward compatibility)
        crop = None
        
        # Try trace_id first
        if trace_id.isdigit():
            cursor.execute("""
                SELECT 
                    c.*,
                    u_farmer.name as farmer_name,
                    u_owner.name as current_owner_name
                FROM crops c
                LEFT JOIN users u_farmer ON c.farmer_id = u_farmer.id
                LEFT JOIN users u_owner ON c.current_owner_id = u_owner.id
                WHERE c.trace_id = %s
            """, (trace_id,))
            crop = cursor.fetchone()
        
        # If not found by trace_id and it's a number, try as crop_id (backward compatibility)
        if not crop and trace_id.isdigit():
            cursor.execute("""
                SELECT 
                    c.*,
                    u_farmer.name as farmer_name,
                    u_owner.name as current_owner_name
                FROM crops c
                LEFT JOIN users u_farmer ON c.farmer_id = u_farmer.id
                LEFT JOIN users u_owner ON c.current_owner_id = u_owner.id
                WHERE c.id = %s
            """, (int(trace_id),))
            crop = cursor.fetchone()
        
        if not crop:
            return jsonify({"error": "Product not found. Please check the Trace ID."}), 404

        # Build the transaction chain by following the ownership path
        # This traces ONLY this specific product's journey, not all products from the farmer
        
        # Start with transactions for this specific crop
        cursor.execute("""
            SELECT 
                t.*,
                u_from.name as from_user_name,
                u_from.role as from_user_role,
                u_to.name as to_user_name,
                u_to.role as to_user_role
            FROM transactions t
            JOIN users u_from ON t.from_user_id = u_from.id
            JOIN users u_to ON t.to_user_id = u_to.id
            WHERE t.crop_id = %s
            ORDER BY t.timestamp ASC
        """, (crop['id'],))
        
        transactions = cursor.fetchall()

        # Build journey timeline
        journey = []
        
        # Add initial creation by farmer
        journey.append({
            "step": 1,
            "action": "crop_created",
            "user_name": crop['farmer_name'],
            "user_role": "farmer",
            "timestamp": crop['created_at'].isoformat() if crop['created_at'] else None,
            "description": f"Farmer {crop['farmer_name']} added {crop['quantity']} {crop['unit']} of {crop['name']} to the system"
        })

        # Add all transactions, filtering to show only relevant ones to this trace_id
        # (skip intermediate partial purchase splits, show the chain that led to this product)
        added_steps = set()  # Track which transactions we've added
        
        for transaction in transactions:
            # Skip if we already added this transaction
            tx_key = f"{transaction['from_user_id']}_{transaction['to_user_id']}_{transaction['timestamp']}"
            if tx_key in added_steps:
                continue
                
            action_map = {
                'farmer_to_retailer': f"Sold to retailer {transaction['to_user_name']}",
                'retailer_to_distributor': f"Distributed to {transaction['to_user_name']}",
                'distributor_to_customer': f"Delivered to customer {transaction['to_user_name']}"
            }
            
            journey.append({
                "step": len(journey) + 1,
                "action": transaction['transaction_type'],
                "from_user_name": transaction['from_user_name'],
                "from_user_role": transaction['from_user_role'],
                "to_user_name": transaction['to_user_name'],
                "to_user_role": transaction['to_user_role'],
                "quantity": float(transaction['quantity']),
                "price": float(transaction['price']),
                "timestamp": transaction['timestamp'].isoformat() if transaction['timestamp'] else None,
                "block_hash": transaction['block_hash'],
                "description": action_map.get(transaction['transaction_type'], "Transaction completed")
            })
            
            added_steps.add(tx_key)

        cursor.close()
        conn.close()

        return jsonify({
            "crop": {
                "id": crop['id'],
                "trace_id": crop['trace_id'],
                "name": crop['name'],
                "description": crop['description'],
                "current_owner": crop['current_owner_name'],
                "current_status": crop['status'],
                "image_path": crop['image_path']
            },
            "journey": journey,
            "total_steps": len(journey)
        }), 200

    except Exception as e:
        print(f"Error fetching crop journey: {str(e)}")
        return jsonify({"error": "Failed to fetch crop journey"}), 500

@trace_bp.route('/blockchain/<string:block_hash>', methods=['GET'])
def get_block_details(block_hash):
    """Get details of a specific blockchain block"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check transactions table
        cursor.execute("SELECT * FROM transactions WHERE block_hash = %s", (block_hash,))
        transaction = cursor.fetchone()

        if transaction:
            cursor.close()
            conn.close()
            return jsonify({
                "block_hash": block_hash,
                "type": "transaction",
                "data": transaction
            }), 200

        # Check blocks table
        cursor.execute("SELECT * FROM blocks WHERE hash = %s", (block_hash,))
        block = cursor.fetchone()

        if block:
            cursor.close()
            conn.close()
            return jsonify({
                "block_hash": block_hash,
                "type": "block",
                "data": block
            }), 200

        cursor.close()
        conn.close()
        return jsonify({"error": "Block not found"}), 404

    except Exception as e:
        print(f"Error fetching block details: {str(e)}")
        return jsonify({"error": "Failed to fetch block details"}), 500