from flask import Blueprint, jsonify, request
from database import get_db_connection
from middleware.auth_middleware import token_required
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics based on user role"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        stats = {}
        
        if current_user['role'] == 'farmer':
            # Farmer statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_crops,
                    SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available_crops,
                    SUM(CASE WHEN status = 'sold' THEN 1 ELSE 0 END) as sold_crops,
                    SUM(quantity) as total_quantity,
                    AVG(price_per_unit) as avg_price
                FROM crops
                WHERE farmer_id = %s
            """, (current_user['id'],))
            crop_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(price) as total_revenue
                FROM transactions
                WHERE from_user_id = %s
            """, (current_user['id'],))
            transaction_stats = cursor.fetchone()
            
            # Recent transactions
            cursor.execute("""
                SELECT 
                    t.*,
                    c.name as crop_name,
                    u.name as buyer_name
                FROM transactions t
                JOIN crops c ON t.crop_id = c.id
                JOIN users u ON t.to_user_id = u.id
                WHERE t.from_user_id = %s
                ORDER BY t.timestamp DESC
                LIMIT 5
            """, (current_user['id'],))
            recent_transactions = cursor.fetchall()
            
            stats = {
                "role": "farmer",
                "crops": {
                    "total": crop_stats['total_crops'] or 0,
                    "available": crop_stats['available_crops'] or 0,
                    "sold": crop_stats['sold_crops'] or 0,
                    "total_quantity": float(crop_stats['total_quantity'] or 0),
                    "avg_price": float(crop_stats['avg_price'] or 0)
                },
                "transactions": {
                    "total": transaction_stats['total_transactions'] or 0,
                    "total_revenue": float(transaction_stats['total_revenue'] or 0)
                },
                "recent_transactions": [
                    {
                        "id": t['id'],
                        "crop_name": t['crop_name'],
                        "buyer_name": t['buyer_name'],
                        "quantity": float(t['quantity']),
                        "price": float(t['price']),
                        "timestamp": t['timestamp'].isoformat() if t['timestamp'] else None
                    }
                    for t in recent_transactions
                ]
            }
            
        elif current_user['role'] == 'retailer':
            # Retailer statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_purchases,
                    SUM(price) as total_spent,
                    AVG(price) as avg_purchase_price
                FROM transactions
                WHERE to_user_id = %s AND transaction_type = 'farmer_to_retailer'
            """, (current_user['id'],))
            purchase_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(price) as total_revenue
                FROM transactions
                WHERE from_user_id = %s AND transaction_type = 'retailer_to_distributor'
            """, (current_user['id'],))
            sale_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) as inventory_count
                FROM crops
                WHERE current_owner_id = %s AND status = 'sold'
            """, (current_user['id'],))
            inventory = cursor.fetchone()
            
            stats = {
                "role": "retailer",
                "purchases": {
                    "total": purchase_stats['total_purchases'] or 0,
                    "total_spent": float(purchase_stats['total_spent'] or 0),
                    "avg_price": float(purchase_stats['avg_purchase_price'] or 0)
                },
                "sales": {
                    "total": sale_stats['total_sales'] or 0,
                    "total_revenue": float(sale_stats['total_revenue'] or 0)
                },
                "inventory": {
                    "count": inventory['inventory_count'] or 0
                }
            }
            
        elif current_user['role'] == 'distributor':
            # Distributor statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_purchases,
                    SUM(price) as total_spent
                FROM transactions
                WHERE to_user_id = %s AND transaction_type = 'retailer_to_distributor'
            """, (current_user['id'],))
            purchase_stats = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(price) as total_revenue
                FROM transactions
                WHERE from_user_id = %s AND transaction_type = 'distributor_to_customer'
            """, (current_user['id'],))
            sale_stats = cursor.fetchone()
            
            stats = {
                "role": "distributor",
                "purchases": {
                    "total": purchase_stats['total_purchases'] or 0,
                    "total_spent": float(purchase_stats['total_spent'] or 0)
                },
                "sales": {
                    "total": sale_stats['total_sales'] or 0,
                    "total_revenue": float(sale_stats['total_revenue'] or 0)
                }
            }
            
        elif current_user['role'] == 'customer':
            # Customer statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_purchases,
                    SUM(price) as total_spent,
                    AVG(price) as avg_purchase_price
                FROM transactions
                WHERE to_user_id = %s AND transaction_type = 'distributor_to_customer'
            """, (current_user['id'],))
            purchase_stats = cursor.fetchone()
            
            stats = {
                "role": "customer",
                "purchases": {
                    "total": purchase_stats['total_purchases'] or 0,
                    "total_spent": float(purchase_stats['total_spent'] or 0),
                    "avg_price": float(purchase_stats['avg_purchase_price'] or 0)
                }
            }
        
        cursor.close()
        conn.close()
        
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"Error fetching analytics: {str(e)}")
        return jsonify({"error": "Failed to fetch analytics"}), 500

@analytics_bp.route('/sales-report', methods=['GET'])
@token_required
def get_sales_report(current_user):
    """Get sales report with time period filter"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if current_user['role'] == 'farmer':
            cursor.execute("""
                SELECT 
                    DATE(t.timestamp) as date,
                    COUNT(*) as transaction_count,
                    SUM(t.price) as total_revenue,
                    SUM(t.quantity) as total_quantity
                FROM transactions t
                WHERE t.from_user_id = %s 
                AND t.timestamp >= %s
                GROUP BY DATE(t.timestamp)
                ORDER BY date DESC
            """, (current_user['id'], start_date))
            
        elif current_user['role'] == 'retailer':
            cursor.execute("""
                SELECT 
                    DATE(t.timestamp) as date,
                    COUNT(*) as transaction_count,
                    SUM(t.price) as total_revenue,
                    SUM(t.quantity) as total_quantity
                FROM transactions t
                WHERE t.from_user_id = %s 
                AND t.transaction_type = 'retailer_to_distributor'
                AND t.timestamp >= %s
                GROUP BY DATE(t.timestamp)
                ORDER BY date DESC
            """, (current_user['id'], start_date))
            
        elif current_user['role'] == 'distributor':
            cursor.execute("""
                SELECT 
                    DATE(t.timestamp) as date,
                    COUNT(*) as transaction_count,
                    SUM(t.price) as total_revenue,
                    SUM(t.quantity) as total_quantity
                FROM transactions t
                WHERE t.from_user_id = %s 
                AND t.transaction_type = 'distributor_to_customer'
                AND t.timestamp >= %s
                GROUP BY DATE(t.timestamp)
                ORDER BY date DESC
            """, (current_user['id'], start_date))
        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid role for sales report"}), 403
        
        report = cursor.fetchall()
        
        formatted_report = [
            {
                "date": r['date'].isoformat() if r['date'] else None,
                "transaction_count": r['transaction_count'],
                "total_revenue": float(r['total_revenue'] or 0),
                "total_quantity": float(r['total_quantity'] or 0)
            }
            for r in report
        ]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "period_days": days,
            "report": formatted_report
        }), 200
        
    except Exception as e:
        print(f"Error generating sales report: {str(e)}")
        return jsonify({"error": "Failed to generate sales report"}), 500

