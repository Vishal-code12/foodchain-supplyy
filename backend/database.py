import os
import mysql.connector
from config import Config

def get_db_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )

def init_db():
    """Initialize the database with the schema."""
    # Get the path to schema.sql (one level up from backend directory)
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    schema_path = os.path.join(project_root, 'database', 'schema.sql')
    migrations_dir = os.path.join(project_root, 'database', 'migrations')
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        # If database doesn't exist, create it first
        if e.errno == 1049:  # Unknown database error
            # Connect without specifying database
            temp_conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                port=Config.MYSQL_PORT
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
            temp_cursor.close()
            temp_conn.close()
            # Now reconnect with database
            conn = get_db_connection()
            cursor = conn.cursor()
        else:
            raise

    # Read the schema.sql file and execute it
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Split by semicolon and execute each command
        # Filter out empty commands and comments
        commands = []
        for cmd in sql_script.split(';'):
            cmd = cmd.strip()
            # Skip empty commands and single-line comments
            if cmd and not cmd.startswith('--'):
                # Remove inline comments
                lines = cmd.split('\n')
                cleaned_lines = [line.split('--')[0].strip() for line in lines if line.strip() and not line.strip().startswith('--')]
                cleaned_cmd = ' '.join(cleaned_lines)
                if cleaned_cmd:
                    commands.append(cleaned_cmd)
        
        for command in commands:
            # Skip USE statements as we're already connected to the database
            if command.upper().startswith('USE'):
                continue
            # Skip CREATE DATABASE as it's handled above if needed
            if command.upper().startswith('CREATE DATABASE'):
                continue
            if command:
                try:
                    cursor.execute(command)
                except mysql.connector.Error as e:
                    # Ignore "table already exists" and "duplicate entry" errors
                    if e.errno in [1050, 1062]:  # Table already exists, Duplicate entry
                        continue
                    else:
                        print(f"Warning: Error executing command: {command[:50]}... Error: {e}")
        
        # Run migrations
        if os.path.exists(migrations_dir):
            migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
            for migration_file in migration_files:
                migration_path = os.path.join(migrations_dir, migration_file)
                try:
                    with open(migration_path, 'r', encoding='utf-8') as f:
                        migration_sql = f.read()
                    
                    migration_commands = []
                    for cmd in migration_sql.split(';'):
                        cmd = cmd.strip()
                        if cmd and not cmd.startswith('--'):
                            lines = cmd.split('\n')
                            cleaned_lines = [line.split('--')[0].strip() for line in lines if line.strip() and not line.strip().startswith('--')]
                            cleaned_cmd = ' '.join(cleaned_lines)
                            if cleaned_cmd:
                                migration_commands.append(cleaned_cmd)
                    
                    # Execute commands sequentially - commit after column is added
                    for i, command in enumerate(migration_commands):
                        if command.upper().startswith('USE'):
                            continue
                        try:
                            cursor.execute(command)
                            # Commit after adding column to ensure it exists for next commands
                            if 'ADD COLUMN' in command.upper():
                                conn.commit()
                                print(f"Info: Successfully executed: {command[:50]}...")
                        except mysql.connector.Error as e:
                            # Ignore errors for already existing objects
                            error_codes_to_ignore = [
                                1060,  # Duplicate column name
                                1061,  # Duplicate key name (for indexes/constraints)
                                1050,  # Table already exists
                                1062,  # Duplicate entry
                                1072,  # Key column doesn't exist
                                1068,  # Multiple primary key defined
                                1054,  # Unknown column
                                1065   # Query was empty
                            ]
                            if e.errno in error_codes_to_ignore:
                                print(f"Info: Migration step already completed (or skipped) in {migration_file}: {command[:50]}...")
                                continue
                            else:
                                # Check error message for more context
                                error_msg = str(e).lower()
                                if ('doesn\'t exist' in error_msg or "doesn't exist" in error_msg or 
                                    'unknown column' in error_msg or e.errno == 1072):
                                    # If trying to create constraint/index but column doesn't exist, add column first
                                    if 'trace_id' in error_msg.lower() or 'ADD UNIQUE' in command.upper() or 'CREATE INDEX' in command.upper():
                                        # Check if column exists
                                        try:
                                            cursor.execute("SHOW COLUMNS FROM crops LIKE 'trace_id'")
                                            col_exists = cursor.fetchone()
                                            if not col_exists:
                                                # Column doesn't exist, add it first
                                                cursor.execute("ALTER TABLE crops ADD COLUMN trace_id VARCHAR(20)")
                                                conn.commit()
                                                print(f"Info: Added trace_id column, retrying: {command[:50]}...")
                                                cursor.execute(command)
                                                conn.commit()
                                            else:
                                                # Column exists, constraint/index might already exist
                                                print(f"Info: Column exists, constraint/index may already exist: {command[:50]}...")
                                        except mysql.connector.Error as check_e:
                                            print(f"Warning: Error checking/adding column: {check_e}")
                                    else:
                                        print(f"Warning: Error in migration {migration_file}: {e}")
                                else:
                                    print(f"Warning: Error in migration {migration_file}: {e}")
                except Exception as e:
                    print(f"Warning: Failed to run migration {migration_file}: {e}")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()