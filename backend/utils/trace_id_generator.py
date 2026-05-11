import random
import string
from database import get_db_connection
import mysql.connector

def generate_trace_id():
    """Generate a unique trace ID (minimum 6 digits)"""
    while True:
        # Generate a random 6-8 digit trace ID
        trace_id = ''.join(random.choices(string.digits, k=random.randint(6, 8)))
        
        # Check if it already exists (handle case where column might not exist yet)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM crops WHERE trace_id = %s", (trace_id,))
            exists = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not exists:
                return trace_id
        except mysql.connector.Error as e:
            # If column doesn't exist yet (error 1054), just return the generated ID
            # This can happen if migration hasn't run yet
            if e.errno == 1054:  # Unknown column 'trace_id' in 'where clause'
                print(f"Warning: trace_id column not found. Returning generated ID: {trace_id}")
                return trace_id
            else:
                # For other database errors, re-raise
                raise

