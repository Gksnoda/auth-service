# Architecture

## Overview

Auth Service is a single-tenant authentication provider built with FastAPI.
It handles user registration, login, token management, password recovery, and role-based access control.

## Stack

| Layer    | Technology                   |
| -------- | ---------------------------- |
| Backend  | Python 3.14 + FastAPI        |
| Frontend | HTML + CSS + JavaScript      |
| Database | Supabase (PostgreSQL)        |
| Package  | uv                           |

## Authentication

### Token Strategy

The service uses a dual-token approach with rotation:

- **Access Token (JWT, stateless)**
  - Expiration: 5 minutes
  - Payload: user ID, email, role, expiration
  - Used to authenticate API requests

- **Refresh Token (stateful)**
  - Expiration: 10 minutes
  - Stored in the database
  - Used to obtain new access tokens without re-login
  - **Rotation:** each use invalidates the old token and issues a new one
  - Revoked on logout
  - All tokens invalidated on password change/reset

### Password

- **Hashing:** Argon2id
- **Validation:** minimum 5 characters, no complexity requirements

## Authorization

### Roles

| Role    | Description                                                   |
| ------- | ------------------------------------------------------------- |
| `user`  | Default role. Can access their own data and change password    |
| `admin` | Can do everything a user can, plus create users via email only |

- Role is assigned at user creation (default: `user`)
- Role is included in the access token payload
- Admin-only endpoints require `admin` role validation

### must_change_password Enforcement

Server-side enforcement: users with `must_change_password = true` are blocked from all endpoints except `/auth/change-password` and `/auth/logout` (returns `403 Forbidden`).

## Endpoints

| Endpoint                | Method | Auth Required | Role Required | Description                                  |
| ----------------------- | ------ | ------------- | ------------- | -------------------------------------------- |
| `/auth/register`        | POST   | No            | -             | Register a new user                          |
| `/auth/login`           | POST   | No            | -             | Login and receive tokens                     |
| `/auth/refresh`         | POST   | No            | -             | Rotate tokens (new access + new refresh)     |
| `/auth/logout`          | POST   | Yes           | -             | Revoke refresh token                         |
| `/auth/forgot-password` | POST   | No            | -             | Request password reset email                 |
| `/auth/reset-password`  | POST   | No            | -             | Reset password with token from email         |
| `/auth/change-password` | POST   | Yes           | -             | Change own password (forced after temp pass) |
| `/admin/create-user`    | POST   | Yes           | `admin`       | Create user by email with temporary password |

## Security

### Rate Limiting

| Endpoint                | Limit              | Strategy       |
| ----------------------- | ------------------ | -------------- |
| `/auth/login`           | 5 attempts / 5 min | Per IP + email |
| `/auth/register`        | 5 attempts / 5 min | Per IP         |
| `/auth/forgot-password` | 5 attempts / 5 min | Per IP         |

### Temporary Password Flow

1. Admin creates user via `/admin/create-user` providing only the email
2. Server generates a strong temporary password
3. User logs in with temporary password
4. Server blocks all requests (except change-password and logout) until password is changed
5. User changes password, all previous refresh tokens are invalidated

## Email

Provider to be defined. Options for development:

- **Mailtrap** — Free tier, email sandbox for testing
- **Resend** — Free tier (100 emails/day)
- **MailHog** — Local SMTP server with web UI

The email service must be abstracted so the provider can be easily swapped.

## Frontend Pages

| Page                    | Description                              |
| ----------------------- | ---------------------------------------- |
| Login                   | Email and password form                  |
| Register                | New user registration form               |
| Forgot Password         | Request password reset                   |
| Change Password         | Form to set new password                 |
| Home                    | Authenticated area (post-login)          |

## Project Structure

To be defined.
