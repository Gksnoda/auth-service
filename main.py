from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailRequest(BaseModel):
    email: EmailStr


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/auth/login")
def login(body: EmailRequest):
    return {"message": f"Email {body.email} received"}
