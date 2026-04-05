import os

import bcrypt
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client

load_dotenv()

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailRequest(BaseModel):
    email: EmailStr


class CreateAccountRequest(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/login")
def login(body: EmailRequest):
    return {"message": f"Email {body.email} received"}


@app.post("/auth/register")
def register(body: CreateAccountRequest):
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt())

    supabase.table("users").insert({
        "email": body.email,
        "password_hash": hashed.decode(),
        "name": body.name,
    }).execute()

    return {"message": "Account created"}
