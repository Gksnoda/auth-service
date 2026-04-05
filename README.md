# Auth Service

An authentication service provider built with FastAPI, inspired by providers like Entra and Cognito.

## Stack

- **Backend:** Python 3.14 + FastAPI
- **Frontend:** HTML + CSS + JavaScript (vanilla)
- **Database:** Supabase (PostgreSQL)
- **Package Manager:** uv

## Features

- User registration
- Login with email/password
- JWT authentication (access token + refresh token)
- Refresh token rotation (stateful, stored in database)
- Logout (refresh token revocation)
- Forgot password (with email sending)
- Admin-generated temporary password (user must change on first login)
- Role-based access control (user and admin roles)
- Rate limiting on login (5 attempts per 5 minutes)

## Architecture

### Authentication Flow

- **Access Token:** Short-lived JWT containing user ID, email, role and expiration
- **Refresh Token:** Long-lived, stored in the database, used to obtain new access tokens
- **Password Hashing:** Argon2id

### Frontend Pages

- Login
- Register
- Forgot Password
- Change Temporary Password
- Home (authenticated area)

## Setup

```bash
uv sync
```

## Running

```bash
uv run fastapi dev
```
