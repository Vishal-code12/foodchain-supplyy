#!/usr/bin/env python3
"""
Database Reset Script
Clears all data from blocks, transactions, and crops tables
Keeps schema and users intact
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

from database import get_db_connection

def reset_database():
    """Reset tables: blocks, transactions, crops"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔄 Starting database reset...")
        
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Clear blocks table
        print("  • Clearing blocks table...")
        cursor.execute("DELETE FROM blocks")
        cursor.execute("ALTER TABLE blocks AUTO_INCREMENT = 1")
        
        # Clear transactions table
        print("  • Clearing transactions table...")
        cursor.execute("DELETE FROM transactions")
        cursor.execute("ALTER TABLE transactions AUTO_INCREMENT = 1")
        
        # Clear crops table
        print("  • Clearing crops table...")
        cursor.execute("DELETE FROM crops")
        cursor.execute("ALTER TABLE crops AUTO_INCREMENT = 1")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Verify
        cursor.execute("SELECT COUNT(*) as count FROM blocks")
        blocks_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM transactions")
        transactions_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM crops")
        crops_count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✅ Database reset complete!")
        print(f"   • blocks: {blocks_count} rows")
        print(f"   • transactions: {transactions_count} rows")
        print(f"   • crops: {crops_count} rows")
        print("\n📝 Users table: UNCHANGED")
        print("📝 Schema: UNCHANGED")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during reset: {str(e)}")
        return False

if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
