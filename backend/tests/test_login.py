from unittest.mock import MagicMock, patch

import jwt
import pytest
from argon2.exceptions import VerifyMismatchError
from fastapi.testclient import TestClient

from main import JWT_ALGORITHM, JWT_SECRET, app

client = TestClient(app)


def _mock_supabase_select(mock_supabase, data=None):
    mock_chain = MagicMock()
    mock_supabase.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.execute.return_value = MagicMock(data=data or [])
    return mock_chain


@patch("main.ph")
@patch("main.supabase")
def test_login_returns_access_token(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
        "name": "Test User",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@patch("main.ph")
@patch("main.supabase")
def test_login_token_has_expected_claims(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    token = response.json()["access_token"]
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    assert decoded["sub"] == "user-42"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "user"
    assert "iat" in decoded
    assert "exp" in decoded


@patch("main.ph")
@patch("main.supabase")
def test_login_token_expires_in_15_minutes(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    token = response.json()["access_token"]
    decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    assert decoded["exp"] - decoded["iat"] == 15 * 60


@patch("main.ph")
@patch("main.supabase")
def test_login_token_rejects_wrong_secret(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    token = response.json()["access_token"]
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, "wrong-secret", algorithms=[JWT_ALGORITHM])


@patch("main.ph")
@patch("main.supabase")
def test_login_user_not_found(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[])

    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })

    assert response.status_code == 401
    # Timing-attack protection: ph.verify must run even when the user does not
    # exist, so both branches take the same time.
    mock_ph.verify.assert_called_once()


@patch("main.ph")
@patch("main.supabase")
def test_login_wrong_password(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.side_effect = VerifyMismatchError()

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })

    assert response.status_code == 401


@patch("main.ph")
@patch("main.supabase")
def test_login_same_error_for_user_not_found_and_wrong_password(mock_supabase, mock_ph):
    # Case 1: wrong password
    _mock_supabase_select(mock_supabase, data=[{
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.side_effect = VerifyMismatchError()
    resp_wrong_pw = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpass",
    })

    # Case 2: user not found
    _mock_supabase_select(mock_supabase, data=[])
    mock_ph.verify.side_effect = None
    resp_not_found = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })

    assert resp_wrong_pw.status_code == resp_not_found.status_code == 401
    assert resp_wrong_pw.json() == resp_not_found.json()


def test_login_invalid_email():
    response = client.post("/auth/login", json={
        "email": "not-an-email",
        "password": "whatever",
    })

    assert response.status_code == 422


def test_login_missing_email():
    response = client.post("/auth/login", json={
        "password": "whatever",
    })

    assert response.status_code == 422


def test_login_missing_password():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
    })

    assert response.status_code == 422


@patch("main.ph")
@patch("main.supabase")
def test_login_returns_refresh_token(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("refresh_token"), str)
    assert len(body["refresh_token"]) > 0


@patch("main.ph")
@patch("main.supabase")
def test_login_persists_refresh_token_in_db(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    assert response.status_code == 200
    tables_accessed = [call.args[0] for call in mock_supabase.table.call_args_list]
    assert "refresh_tokens" in tables_accessed

    mock_chain = mock_supabase.table.return_value
    insert_calls = mock_chain.insert.call_args_list
    assert any(
        call.args
        and isinstance(call.args[0], dict)
        and call.args[0].get("user_id") == "user-42"
        and call.args[0].get("token_hash")
        and call.args[0].get("expires_at")
        for call in insert_calls
    )


@patch("main.ph")
@patch("main.supabase")
def test_login_refresh_token_is_not_stored_in_plaintext(mock_supabase, mock_ph):
    _mock_supabase_select(mock_supabase, data=[{
        "id": "user-42",
        "email": "test@example.com",
        "password_hash": "stored-hash",
    }])
    mock_ph.verify.return_value = True

    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "validpass",
    })

    refresh_token = response.json()["refresh_token"]
    mock_chain = mock_supabase.table.return_value
    insert_calls = mock_chain.insert.call_args_list
    stored_hashes = [
        call.args[0]["token_hash"]
        for call in insert_calls
        if call.args and isinstance(call.args[0], dict) and "token_hash" in call.args[0]
    ]
    assert stored_hashes, "expected at least one insert with a token_hash"
    assert refresh_token not in stored_hashes
