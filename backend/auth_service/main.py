from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import argparse
import uvicorn
import os

from auth_service.auth import verify_credentials, create_jwt, parse_jwt
from auth_service.schemas import LoginRequest, UserPublic

app = FastAPI(title="Auth Service", version="1.0.0")

# Frontend origin for dev (Vite default)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],  # must be explicit for credentialed requests
    allow_credentials=True,           # allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24  # 1 day

def _unpack_sub(sub: str) -> tuple[str, str]:
    """
    sub is stored as '<user_id>|<email>' for simplicity.
    If format differs, do a best-effort guess.
    """
    if not sub:
        return ("", "")
    if "|" in sub:
        uid, email = sub.split("|", 1)
        return (uid, email)
    # fallback: if it *looks* like an email, use it as email
    if "@" in sub:
        return ("00000000-0000-0000-0000-000000000001", sub)
    # otherwise treat as id only
    return (sub, "user@example.com")

def get_current_user(request: Request) -> Optional[UserPublic]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = parse_jwt(token)
    if not payload:
        return None
    sub = payload.get("sub") or ""
    uid, email = _unpack_sub(sub)
    if not uid:
        return None
    return UserPublic(id=uid, email=email)

@app.post("/auth/login", response_model=UserPublic)
def login(payload: LoginRequest, response: Response):
    """
    Verifies credentials. On success, sets an HttpOnly cookie with the JWT.
    Returns a minimal user object (no token in body).
    """
    user = verify_credentials(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Encode both id and email into sub so we can reconstruct the user from the cookie later.
    sub_value = f"{user['id']}|{user['email']}"
    token = create_jwt(sub=sub_value)

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,   # True when served over HTTPS
        samesite="lax", # good for same-site dev
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

    # Return basic user info; cookie is what keeps you logged in on reload
    return UserPublic(id=user["id"], email=user["email"])

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}

@app.get("/auth/me", response_model=Optional[UserPublic])
def me(user: Optional[UserPublic] = Depends(get_current_user)):
    return user

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auth Service")
    parser.add_argument("--port", type=int, default=8000, help="Port number to run the service on")
    args = parser.parse_args()

    print(f"Starting Auth Service on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)