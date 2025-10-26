import psycopg2
import os
from typing import Optional

# Database configuration  
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "app_db"),
    "user": os.getenv("DB_USER", "app_user"),
    "password": os.getenv("DB_PASSWORD", "app_pass")
}

def get_db_connection():
    """Get a database connection"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        raise Exception(f"Failed to connect to database: {str(e)}")

def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        conn.close()
        return result[0] == 1
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False
