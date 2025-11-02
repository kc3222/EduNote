import os
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
from passlib.context import CryptContext
from auth_service.database import get_db_cursor

# ---------- Password hashing ----------
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain or "")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain or "", hashed or "")
    except Exception:
        return False

# ---------- Database user lookup ----------
def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Query the database for a user by email.
    Returns user dict with 'id', 'email', 'password_hash' if found, else None.
    """
    conn, cur = get_db_cursor()
    try:
        cur.execute("SELECT id, email, password FROM app_user WHERE email = %s", (email,))
        row = cur.fetchone()
        if not row:
            return None
        # Convert row to dict
        return {
            "id": str(row["id"]),  # Ensure UUID is string
            "email": row["email"],
            "password_hash": row["password"],  # Database stores as 'password'
        }
    except Exception as e:
        print(f"Error querying user: {e}")
        return None
    finally:
        cur.close()
        conn.close()

def verify_credentials(email: str, password: str) -> Optional[Dict]:
    """
    Verify credentials against database.
    Return full user dict (with 'id', 'email', 'password_hash') if valid, else None.
    """
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["password_hash"]):
        return None
    
    return user

def user_id_for_email(email: str) -> Optional[str]:
    """
    Get user ID from database for a given email.
    Returns the user ID if found, otherwise returns None.
    """
    user = get_user_by_email(email)
    if user:
        return user["id"]
    return None

def create_user(email: str, password: str) -> Optional[Dict]:
    """
    Create a new user in the database.
    Returns user dict with 'id', 'email', 'password_hash' if successful, else None.
    """
    import uuid
    conn, cur = get_db_cursor()
    try:
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return None
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        cur.execute(
            "INSERT INTO app_user (id, email, password) VALUES (%s, %s, %s)",
            (user_id, email, password_hash)
        )
        conn.commit()
        
        return {
            "id": user_id,
            "email": email,
            "password_hash": password_hash
        }
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.rollback()
        return None
    finally:
        cur.close()
        conn.close()

# ---------- JWT ----------
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
JWT_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "120"))

def create_jwt(sub: str) -> str:
    now = datetime.utcnow()
    payload = {"sub": sub, "iat": now, "exp": now + timedelta(minutes=JWT_EXP_MIN)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def parse_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception:
        return None