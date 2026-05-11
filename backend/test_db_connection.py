import mysql.connector

def test_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # 🔹 change if needed
            password="Satheesh@11",          # 🔹 add your MySQL password if any
            database="foodchain_db"
        )

        if connection.is_connected():
            print("✅ Database connection successful!")
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("📋 Tables in your database:")
            for t in tables:
                print(" -", t[0])

    except mysql.connector.Error as err:
        print("❌ Database connection failed:")
        print("Error:", err)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔒 Connection closed.")


if __name__ == "__main__":
    test_connection()
