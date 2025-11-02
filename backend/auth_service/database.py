import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'app_db'),
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'app_pass')
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DATABASE_CONFIG)
def get_db_cursor():
    """Get database cursor with dict-like access"""
    conn = get_db_connection()
    return conn, conn.cursor(cursor_factory=RealDictCursor)

