# Overview

## System Description

Auth Service is a single-tenant authentication provider that handles user registration, login, token management, password recovery, and role-based access control.

## Roles

| Role    | Description                                                   |
| ------- | ------------------------------------------------------------- |
| `user`  | Default role. Can access their own data and change password    |
| `admin` | Can do everything a user can, plus create users via email only |

## Token Strategy

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant DB as Database

    C->>S: POST /auth/login (email, password)
    S->>DB: Validate credentials
    DB-->>S: User data
    S-->>C: Access Token (JWT) + Refresh Token

    Note over C: Access Token expires (5 min)

    C->>S: POST /auth/refresh (refresh_token)
    S->>DB: Validate refresh token
    S->>DB: Revoke old refresh token
    S->>DB: Store new refresh token
    S-->>C: New Access Token + New Refresh Token

    C->>S: POST /auth/logout (refresh_token)
    S->>DB: Revoke refresh token
    S-->>C: 200 OK
```

### Access Token (JWT, stateless)

- **Expiration:** 5 minutes
- Payload: `user_id`, `email`, `role`, `exp`
- Sent via `Authorization: Bearer <token>` header
- Not stored in the database

### Refresh Token (stateful)

- **Expiration:** 10 minutes
- Stored in the database
- Used to get a new access token without re-login
- **Rotation:** each use invalidates the old refresh token and issues a new one
- Revoked on logout
- **All refresh tokens are invalidated** when password is changed or reset

## Password

### Hashing

- Algorithm: **Argon2id**
- All passwords are hashed before storage
- Plain text passwords are never stored or logged

### Validation

- Minimum length: **5 characters**
- No complexity requirements

## Endpoints Summary

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

## General Flow

```mermaid
flowchart TD
    A[User] -->|Register| B[POST /auth/register]
    B --> C[POST /auth/login]
    A -->|Login| C
    C -->|Success| D{must_change_password?}
    D -->|Yes| E[POST /auth/change-password]
    D -->|No| F[Authenticated Area]
    E -->|Password changed| F
    F -->|Token expired| G[POST /auth/refresh]
    G -->|New access + refresh token| F
    F -->|Logout| H[POST /auth/logout]
    A -->|Forgot password| I[POST /auth/forgot-password]
    I -->|Email sent| J[POST /auth/reset-password]
    J -->|Password reset| C

    AD[Admin] -->|Create user by email| K[POST /admin/create-user]
    K -->|Temporary password generated| C
```

## must_change_password Enforcement

When a user has `must_change_password = true`, the **server** blocks all requests except:

- `POST /auth/change-password`
- `POST /auth/logout`

Any other authenticated request returns `403 Forbidden` with a message indicating the user must change their password first.

```mermaid
flowchart TD
    R[Authenticated Request] --> M{must_change_password?}
    M -->|No| P[Process request normally]
    M -->|Yes| E{Is endpoint allowed?}
    E -->|/auth/change-password or /auth/logout| P
    E -->|Any other endpoint| B[403 Forbidden]
```

## Temporary Password Flow

```mermaid
sequenceDiagram
    participant AD as Admin
    participant S as Server
    participant DB as Database
    participant U as User

    AD->>S: POST /admin/create-user (email)
    S->>S: Generate strong temporary password
    S->>DB: Create user (must_change_password = true)
    S-->>AD: 201 Created (temporary password)

    U->>S: POST /auth/login (email, temp_password)
    S->>DB: Validate credentials
    S-->>U: Access Token + Refresh Token + must_change_password: true

    Note over U: Server blocks all requests except change-password and logout

    U->>S: POST /auth/change-password (new_password)
    S->>DB: Update password, set must_change_password = false
    S->>DB: Invalidate all existing refresh tokens
    S-->>U: 200 OK + New Access Token + New Refresh Token
```

## Forgot Password Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Server
    participant DB as Database
    participant E as Email Service

    U->>S: POST /auth/forgot-password (email)
    S->>DB: Find user by email
    S->>DB: Store reset token (with expiration)
    S->>E: Send reset email with token
    S-->>U: 200 OK (always, even if email not found)

    U->>S: POST /auth/reset-password (token, new_password)
    S->>DB: Validate reset token
    alt Token valid
        S->>DB: Update password, invalidate token
        S->>DB: Invalidate all refresh tokens
        S-->>U: 200 OK
    else Token invalid or expired
        S-->>U: 400 Bad Request
    end
```

## Rate Limiting

| Endpoint                | Limit              | Strategy       |
| ----------------------- | ------------------ | -------------- |
| `/auth/login`           | 5 attempts / 5 min | Per IP + email |
| `/auth/register`        | 5 attempts / 5 min | Per IP         |
| `/auth/forgot-password` | 5 attempts / 5 min | Per IP         |

When the limit is reached, the server responds with `429 Too Many Requests`.

## Email

Provider to be defined. Options for development:

- **Mailtrap** — Free tier, email sandbox for testing
- **Resend** — Free tier (100 emails/day)
- **MailHog** — Local SMTP server with web UI

The email service must be abstracted so the provider can be easily swapped.
