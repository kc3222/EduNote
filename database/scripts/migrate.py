#!/usr/bin/env python3
import os
import sys
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'app_db',
    'user': 'app_user',
    'password': 'app_pass'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_migrations_table():
    """Create migrations tracking table if it doesn't exist"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    conn.close()

def get_applied_migrations():
    """Get list of already applied migrations"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM migrations ORDER BY id")
    applied = [row[0] for row in cur.fetchall()]
    conn.close()
    return applied

def get_next_migration_number():
    """Get the next migration number based on existing files"""
    if not os.path.exists('migrations'):
        return 1
    
    migration_files = [f for f in os.listdir('migrations') if f.endswith('.sql')]
    if not migration_files:
        return 1
    
    # Extract numbers from existing files
    numbers = []
    for filename in migration_files:
        try:
            # Extract number from format: 001_description.sql
            number = int(filename.split('_')[0])
            numbers.append(number)
        except (ValueError, IndexError):
            continue
    
    return max(numbers) + 1 if numbers else 1

def apply_migration(filename):
    """Apply a single migration file"""
    migration_path = os.path.join('migrations', filename)
    
    if not os.path.exists(migration_path):
        print(f"Migration file {filename} not found!")
        return False
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        cur.execute(sql)
        cur.execute("INSERT INTO migrations (filename) VALUES (%s)", (filename,))
        conn.commit()
        print(f"✅ Applied migration: {filename}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to apply {filename}: {e}")
        return False
    finally:
        conn.close()

def migrate():
    """Run all pending migrations"""
    create_migrations_table()
    applied = get_applied_migrations()
    
    migration_files = sorted([f for f in os.listdir('migrations') if f.endswith('.sql')])
    pending = [f for f in migration_files if f not in applied]
    
    if not pending:
        print("No pending migrations")
        return
    
    print(f"Found {len(pending)} pending migrations:")
    for f in pending:
        print(f"  - {f}")
    
    for filename in pending:
        if not apply_migration(filename):
            print("Migration failed. Stopping.")
            sys.exit(1)
    
    print("All migrations completed!")

def create_migration(name):
    """Create a new migration file with incremental numbering"""
    next_number = get_next_migration_number()
    filename = f"{next_number:03d}_{name}.sql"
    filepath = os.path.join('migrations', filename)
    
    with open(filepath, 'w') as f:
        f.write(f"-- Migration: {name}\n")
        f.write(f"-- Created: {datetime.now().isoformat()}\n\n")
        f.write("-- Add your SQL here\n")
    
    print(f"Created migration: {filename}")
    return filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [migrate|create <name>]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate":
        migrate()
    elif command == "create" and len(sys.argv) > 2:
        create_migration(sys.argv[2])
    else:
        print("Usage: python migrate.py [migrate|create <name>]")