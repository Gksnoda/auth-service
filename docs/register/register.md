# Register

## Logic

1. The user submits their email, password, and optionally a name
2. The server receives the request at `POST /auth/register`
3. The password is hashed using bcrypt with an auto-generated salt
4. The user data (email, password hash, and name) is inserted into the `users` table in Supabase
5. The server returns a success message

## Diagram

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API as FastAPI
    participant Bcrypt
    participant DB as Supabase

    User->>Frontend: fills email, password, name (optional)
    Frontend->>API: POST /auth/register {email, password, name}
    API->>Bcrypt: hashpw(password, gensalt())
    Bcrypt-->>API: password_hash
    API->>DB: INSERT into users (email, password_hash, name)
    DB-->>API: success
    API-->>Frontend: {"message": "Account created"}
    Frontend-->>User: account created
```
