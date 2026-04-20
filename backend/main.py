import hashlib
import os
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client

load_dotenv()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=7)
REFRESH_TOKEN_BYTES = 32

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CreateAccountRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5, max_length=50)
    name: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


ph = PasswordHasher()
# Precomputed hash used to keep login timing constant when the email does not
# exist, so attackers cannot enumerate accounts by measuring response time.
DUMMY_HASH = ph.hash("dummy-password-for-timing")


def _create_access_token(user: dict) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user.get("role", "user"),
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _create_refresh_token(user_id: str) -> str:
    raw_token = secrets.token_urlsafe(REFRESH_TOKEN_BYTES)
    expires_at = datetime.now(UTC) + REFRESH_TOKEN_TTL
    supabase.table("refresh_tokens").insert({
        "user_id": user_id,
        "token_hash": _hash_refresh_token(raw_token),
        "expires_at": expires_at.isoformat(),
    }).execute()
    return raw_token


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/login")
def login(body: LoginRequest):
    result = supabase.table("users").select("*").eq("email", body.email).execute()

    if not result.data:
        try:
            ph.verify(DUMMY_HASH, body.password)
        except VerifyMismatchError:
            pass
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = result.data[0]
    try:
        ph.verify(user["password_hash"], body.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid email or password") from None

    access_token = _create_access_token(user)
    refresh_token = _create_refresh_token(user["id"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/refresh")
def refresh(body: RefreshRequest):
    token_hash = _hash_refresh_token(body.refresh_token)
    result = (
        supabase.table("refresh_tokens")
        .select("*")
        .eq("token_hash", token_hash)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_row = result.data[0]
    if token_row.get("revoked_at") is not None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_at = datetime.fromisoformat(token_row["expires_at"])
    if expires_at <= datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    supabase.table("refresh_tokens").update({
        "revoked_at": datetime.now(UTC).isoformat(),
    }).eq("id", token_row["id"]).execute()

    user_result = (
        supabase.table("users")
        .select("*")
        .eq("id", token_row["user_id"])
        .execute()
    )
    if not user_result.data:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = user_result.data[0]
    access_token = _create_access_token(user)
    new_refresh_token = _create_refresh_token(user["id"])

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@app.post("/auth/register", status_code=201)
def register(body: CreateAccountRequest):
    hashed = ph.hash(body.password)

    try:
        supabase.table("users").insert({
            "email": body.email,
            "password_hash": hashed,
            "name": body.name,
        }).execute()
    except Exception as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already exists") from None
        raise

    return {"message": "Account created"}
