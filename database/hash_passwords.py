#!/usr/bin/env python3
"""
Script to hash passwords in the database for existing users.
Run this after updating auth service to use database.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'app_db'),
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'app_pass')
}

def hash_user_passwords():
    """Hash passwords for all users that have plain text passwords"""
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get all users
        cur.execute("SELECT id, email, password FROM app_user")
        users = cur.fetchall()
        
        for user in users:
            password = user['password']
            # Check if password is already hashed (bcrypt hashes start with $2b$ or similar)
            if password.startswith('$2'):
                print(f"Password for {user['email']} is already hashed, skipping")
                continue
            
            # Hash the password
            hashed = pwd_context.hash(password)
            
            # Update the database
            cur.execute(
                "UPDATE app_user SET password = %s WHERE id = %s",
                (hashed, user['id'])
            )
            print(f"Hashed password for {user['email']}")
        
        conn.commit()
        print("✅ All passwords hashed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    hash_user_passwords()

