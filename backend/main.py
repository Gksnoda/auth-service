import os
from datetime import datetime, timedelta, timezone

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


ph = PasswordHasher()
# Precomputed hash used to keep login timing constant when the email does not
# exist, so attackers cannot enumerate accounts by measuring response time.
DUMMY_HASH = ph.hash("dummy-password-for-timing")


def _create_access_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "role": user.get("role", "user"),
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


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
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = _create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


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
            raise HTTPException(status_code=409, detail="Email already exists")
        raise

    return {"message": "Account created"}
