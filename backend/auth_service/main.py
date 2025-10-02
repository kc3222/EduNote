from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

from auth import verify_credentials, create_jwt, parse_jwt
from schemas import LoginRequest, UserPublic

app = FastAPI()

# 👇 Set this to your frontend origin in dev (e.g., Vite default)
FRONTEND_ORIGIN = "http://localhost:5173"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,          # required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

COOKIE_NAME = "access_token"

def get_current_user(request: Request) -> Optional[UserPublic]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    payload = parse_jwt(token)
    if not payload:
        return None
    sub = payload.get("sub")
    # In a real app, fetch user by sub (user_id or email). Here, echo back:
    return UserPublic(id=1, email=sub)

@app.post("/auth/login", response_model=UserPublic)
def login(payload: LoginRequest, response: Response):
    user = verify_credentials(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_jwt(sub=user["email"])
    # 🍪 HttpOnly cookie for security; SameSite/Lax is good for same-site dev
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=False,         # set True on HTTPS
        samesite="lax",       # consider 'strict' or 'none' (+ secure) as needed
        max_age=60*60*24,
        path="/",
    )
    return user

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}

@app.get("/auth/me", response_model=Optional[UserPublic])
def me(user: Optional[UserPublic] = Depends(get_current_user)):
    # Returns user if logged in; null otherwise
    return user

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# Run: uvicorn main:app --reload --port 8000
