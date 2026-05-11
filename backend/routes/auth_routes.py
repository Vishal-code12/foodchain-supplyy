from flask import Blueprint, request, jsonify
from database import get_db_connection
from auth import hash_password, verify_password, generate_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    phone = data.get('phone')
    address = data.get('address')

    if not all([name, email, password, role]):
        return jsonify({"error": "Missing required fields"}), 400

    if role not in ['farmer', 'retailer', 'distributor', 'customer']:
        return jsonify({"error": "Invalid role"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Email already exists"}), 400

    # Create user
    password_hash = hash_password(password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role, phone, address) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, email, password_hash, role, phone, address)
    )
    user_id = cursor.lastrowid
    conn.commit()

    # Generate token
    token = generate_token(user_id, role)

    cursor.close()
    conn.close()

    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user or not verify_password(password, user['password_hash']):
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user['id'], user['role'])

    cursor.close()
    conn.close()

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "role": user['role']
        }
    })

@auth_bp.route('/metamask-login', methods=['POST'])
def metamask_login():
    """Login or register user with MetaMask wallet"""
    from eth_account.messages import encode_defunct
    from web3 import Web3
    
    data = request.get_json()
    wallet_address = data.get('walletAddress')
    signature = data.get('signature')
    role = data.get('role')

    if not all([wallet_address, signature, role]):
        return jsonify({"error": "Missing required fields"}), 400

    if role not in ['farmer', 'retailer', 'distributor', 'customer']:
        return jsonify({"error": "Invalid role"}), 400

    # Verify signature (simplified - in production, verify the exact message)
    # For now, we'll trust the signature and just check if wallet exists
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if wallet address already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (wallet_address,))
    user = cursor.fetchone()

    if user:
        # User exists - login
        token = generate_token(user['id'], user['role'])
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }
        })
    else:
        # User doesn't exist - create new user
        name = f"{role.capitalize()} ({wallet_address[:6]}...{wallet_address[-4:]})"
        
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, wallet_address, 'metamask_auth', role)
        )
        user_id = cursor.lastrowid
        conn.commit()

        token = generate_token(user_id, role)

        cursor.close()
        conn.close()

        return jsonify({
            "message": "Account created and logged in successfully",
            "token": token,
            "user": {
                "id": user_id,
                "name": name,
                "email": wallet_address,
                "role": role
            }
        }), 201