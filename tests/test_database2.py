# test_database.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def test_database_connection():
    print("🧪 Testing Database Connection...")
    
    try:
        # Test basic connection
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"✅ Connected to: {db_version[0]}")
        
        # Test if our database exists
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print(f"✅ Current database: {db_name[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_database_connection():
        print("\n🎉 Database connection successful!")
    else:
        print("\n❌ Fix database connection before proceeding.")