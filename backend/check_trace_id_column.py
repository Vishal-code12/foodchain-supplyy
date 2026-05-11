"""
Script to check if trace_id column exists and add it if it doesn't
Run this to ensure the migration has been applied
"""
from database import get_db_connection
import mysql.connector

def check_and_add_trace_id_column():
    """Check if trace_id column exists, add it if not"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("SHOW COLUMNS FROM crops LIKE 'trace_id'")
        result = cursor.fetchone()
        
        if result:
            print("✓ trace_id column already exists")
        else:
            print("✗ trace_id column not found. Adding it now...")
            try:
                # Add column
                cursor.execute("ALTER TABLE crops ADD COLUMN trace_id VARCHAR(20)")
                conn.commit()
                print("✓ Added trace_id column")
                
                # Add unique constraint
                try:
                    cursor.execute("ALTER TABLE crops ADD UNIQUE (trace_id)")
                    conn.commit()
                    print("✓ Added unique constraint on trace_id")
                except mysql.connector.Error as e:
                    if e.errno in [1061, 1062]:  # Duplicate key
                        print("  Info: Unique constraint may already exist")
                    else:
                        print(f"  Warning: Could not add unique constraint: {e}")
                
                # Create index
                try:
                    cursor.execute("CREATE INDEX idx_trace_id ON crops(trace_id)")
                    conn.commit()
                    print("✓ Created index on trace_id")
                except mysql.connector.Error as e:
                    if e.errno in [1061]:  # Duplicate key name
                        print("  Info: Index may already exist")
                    else:
                        print(f"  Warning: Could not create index: {e}")
                        
            except mysql.connector.Error as e:
                if e.errno == 1060:  # Duplicate column name
                    print("✓ Column already exists (race condition)")
                else:
                    print(f"✗ Error adding column: {e}")
                    raise
        
        cursor.close()
        conn.close()
        print("\n✓ Database check complete!")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    check_and_add_trace_id_column()

