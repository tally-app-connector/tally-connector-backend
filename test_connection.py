import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

try:
    print("Attempting to connect to Neon database...")
    print(f"Host: {os.getenv('DB_HOST')}")
    print(f"Database: {os.getenv('DB_NAME')}")
    print(f"User: {os.getenv('DB_USER')}")
    
    conn = psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
        connect_timeout=30
    )
    
    print("✅ Connection successful!")
    
    cursor = conn.cursor()
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"\n📊 PostgreSQL version: {version[0]}")
    
    # Check tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print("\n📋 Available tables:")
    for table in tables:
        print(f"  ✓ {table[0]}")
    
    # Check users table structure
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'users'
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print("\n📊 Users table structure:")
    for col in columns:
        print(f"  • {col[0]}: {col[1]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ All checks passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()