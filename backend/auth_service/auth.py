import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
from passlib.context import CryptContext

# ---------- Password hashing ----------
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain or "")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain or "", hashed or "")
    except Exception:
        return False

# ---------- Deterministic user id from email ----------
# Use a fixed namespace so the same email -> same UUID every boot.
USER_NS = uuid.UUID("3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a")

def user_id_for_email(email: str) -> str:
    return str(uuid.uuid5(USER_NS, (email or "").strip().lower()))

def make_user(email: str, password_plain: str) -> Dict:
    return {
        "id": user_id_for_email(email),
        "email": email,
        "password_hash": hash_password(password_plain),
    }

# ---------- Demo user (matches your UI) ----------
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "demo@user.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password123")

USERS_BY_EMAIL: Dict[str, Dict] = {
    ADMIN_EMAIL: make_user(ADMIN_EMAIL, ADMIN_PASSWORD)
}

def get_user_by_email(email: str) -> Optional[Dict]:
    return USERS_BY_EMAIL.get(email)

def verify_credentials(email: str, password: str) -> Optional[Dict]:
    """
    Return full user dict (with 'id', 'email', 'password_hash') if valid, else None.
    Guarantees 'id' exists even if the in-memory map was missing it.
    """
    user = get_user_by_email(email)
    if not user:
        return None
    # Hardening: ensure 'id' key exists
    if "id" not in user or not user["id"]:
        user = {**user, "id": user_id_for_email(email)}
        USERS_BY_EMAIL[email] = user  # write back to cache
    if not verify_password(password, user["password_hash"]):
        return None
    return user

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