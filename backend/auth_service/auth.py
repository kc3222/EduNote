import time
from typing import Optional
from jose import jwt, JWTError
from passlib.hash import bcrypt

# ⚙️ ENV/Secrets – keep these in env vars for real apps
JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"
JWT_TTL_SECONDS = 60 * 60 * 24  # 1 day

# Demo user (replace with DB lookup)
DEMO_USER = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "demo@user.com",
    "password_hash": bcrypt.hash("password123"),
}

def verify_credentials(email: str, password: str) -> Optional[dict]:
    if email.lower() == DEMO_USER["email"] and bcrypt.verify(password, DEMO_USER["password_hash"]):
        return {"id": DEMO_USER["id"], "email": DEMO_USER["email"]}
    return None

def create_jwt(sub: str) -> str:
    now = int(time.time())
    payload = {"sub": sub, "iat": now, "exp": now + JWT_TTL_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def parse_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        return None
